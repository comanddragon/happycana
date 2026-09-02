#!/usr/bin/env python
"""
scripts/seed_scraped_products.py

Loads the output of clean_scraped_data.py (clean_data/products.json +
brands.json) into the database.

Safe to run multiple times — everything is keyed by slug/sku and uses
get_or_create / update_or_create.

FEATURE DETECTION
------------------
This script works TODAY, against your backend exactly as it is, by
falling back to the generic `Attribute` EAV table for any field your
models don't have a real column for yet (brand, cannabis type, THC/CBD,
weight, effects, ...). Once you apply backend_patch/*.py and migrate, it
automatically switches to writing the real columns instead — no seed
script changes needed. Every run prints a summary of which fields landed
as native columns vs. EAV fallback, so you can watch that fallback list
shrink as you apply the patch.

USAGE
-----
    python scripts/seed_scraped_products.py \\
        --data-dir /path/to/clean_data \\
        --warehouse-name "Happy Days LI - Farmingdale"

Useful flags:
    --limit N          only seed the first N products (fast smoke test)
    --dry-run           parse + report, write nothing to the database

Images are passed through as external URLs (source_url) — not downloaded
or re-hosted. Requires the small ProductImage.source_url / Brand.logo_url
addition in backend_patch/catalog_models_patch.py; falls back to storing
the URL as an EAV Attribute if that field isn't there yet.
"""

import argparse
import decimal
import json
import os
import sys
import time
from pathlib import Path

# ─── Bootstrap Django ────────────────────────────────────────────────────────
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
import django
django.setup()

from django.db import transaction
from django.utils.text import slugify


# ─── Console helpers ──────────────────────────────────────────────────────────

def log(msg):
    print(f"  \u2714  {msg}")


def warn(msg):
    print(f"  \u26a0  {msg}")


def banner(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# ─── Feature detection ────────────────────────────────────────────────────────
# Figures out, once, which of the fields from MISSING_FIELDS.md actually
# exist on your models yet. Everything downstream checks these flags
# instead of hasattr-ing repeatedly.

class Schema:
    def __init__(self):
        from apps.catalog.models import Product, ProductVariant

        self.Product = Product
        self.ProductVariant = ProductVariant

        try:
            from apps.catalog.models import Brand
            self.Brand = Brand
        except ImportError:
            self.Brand = None

        try:
            from apps.catalog.models import Effect
            self.Effect = Effect
        except ImportError:
            self.Effect = None

        try:
            from apps.catalog.models import Lab
            self.Lab = Lab
        except ImportError:
            self.Lab = None

        product_fields = {f.name for f in Product._meta.get_fields()}
        variant_fields = {f.name for f in ProductVariant._meta.get_fields()}

        self.has_brand_fk = self.Brand is not None and "brand" in product_fields
        self.has_compliance_category = "compliance_category" in product_fields
        self.has_cannabis_type = "cannabis_type" in product_fields
        self.has_sub_type = "sub_type" in product_fields
        self.has_effects_m2m = self.Effect is not None and "effects" in product_fields
        self.has_is_featured = "is_featured" in product_fields
        self.has_is_new = "is_new" in product_fields
        self.has_external_source_id = "external_source_id" in product_fields
        self.has_units_sold_hint = "units_sold_hint" in product_fields
        self.has_weight = "weight_value" in variant_fields and "weight_unit" in variant_fields
        self.has_lab = self.Lab is not None

        from apps.catalog.models import ProductImage
        image_fields = {f.name for f in ProductImage._meta.get_fields()}
        self.has_image_source_url = "source_url" in image_fields
        self.has_brand_logo_url = self.Brand is not None and "logo_url" in {
            f.name for f in self.Brand._meta.get_fields()
        }

    def summary(self):
        checks = [
            ("Brand model + Product.brand FK", self.has_brand_fk),
            ("Product.compliance_category", self.has_compliance_category),
            ("Product.cannabis_type", self.has_cannabis_type),
            ("Product.sub_type", self.has_sub_type),
            ("Effect model + Product.effects M2M", self.has_effects_m2m),
            ("Product.is_featured / is_new", self.has_is_featured and self.has_is_new),
            ("Product.external_source_id", self.has_external_source_id),
            ("ProductVariant.weight_value / weight_unit", self.has_weight),
            ("Lab model (potency/COA)", self.has_lab),
            ("ProductImage.source_url", self.has_image_source_url),
        ]
        banner("Schema detection (see MISSING_FIELDS.md / backend_patch/)")
        for name, present in checks:
            print(f"  [{'x' if present else ' '}] {name}")
        missing = [name for name, present in checks if not present]
        if missing:
            print(f"\n  {len(missing)} field(s) not yet on your models -> falling back to the")
            print("  generic Attribute EAV table for those so no data is lost.")
        else:
            print("\n  All patched fields detected — seeding natively, no EAV fallback needed.")


# ─── EAV fallback helper ──────────────────────────────────────────────────────

class AttributeWriter:
    """Writes a value onto ProductVariant via the existing Attribute/
    AttributeType EAV tables, for any field the schema doesn't have a
    real column for yet. Tracks how many writes it made for the summary."""

    def __init__(self):
        from apps.catalog.models import Attribute, AttributeType
        self.Attribute = Attribute
        self.AttributeType = AttributeType
        self._type_cache = {}
        self.count = 0

    def _get_type(self, name):
        if name not in self._type_cache:
            self._type_cache[name], _ = self.AttributeType.objects.get_or_create(name=name)
        return self._type_cache[name]

    def write(self, variant, type_name, value):
        if value in (None, "", []):
            return
        value = str(value)[:100]
        self.Attribute.objects.update_or_create(
            variant=variant,
            attribute_type=self._get_type(type_name),
            defaults={"value": value},
        )
        self.count += 1



# ─── Core seeding ─────────────────────────────────────────────────────────────

def to_decimal(value, default="0"):
    if value is None:
        return decimal.Decimal(default)
    return decimal.Decimal(str(value))


def unique_slug(model, base_slug, exclude_pk=None):
    slug = base_slug
    n = 2
    qs = model.objects.all()
    while qs.filter(slug=slug).exclude(pk=exclude_pk).exists():
        slug = f"{base_slug}-{n}"
        n += 1
    return slug


def seed_categories(schema, products):
    """Flat categories, one per distinct display category name in the data."""
    from apps.catalog.models import Category

    banner("Categories")
    by_name = {}
    for p in products:
        name = p.get("category_name")
        if name and name not in by_name:
            by_name[name] = p

    categories = {}
    for name in sorted(by_name):
        slug = slugify(name)
        cat, created = Category.objects.get_or_create(
            slug=slug, defaults={"name": name, "is_active": True}
        )
        categories[name] = cat
        log(f"{'created' if created else 'exists '}  {name}")
    return categories


def seed_brands(schema, brands_raw, attr_writer):
    banner("Brands")
    if not schema.has_brand_fk:
        warn(f"No Brand model on your backend yet — {len(brands_raw)} brands from the "
             f"data will be attached to products as an EAV 'Brand' attribute instead. "
             f"Apply backend_patch/catalog_models_patch.py to get a real Brand table.")
        return {}

    brands = {}
    for raw in brands_raw:
        slug = slugify(raw["name"])
        defaults = {
            "name": raw["name"],
            "description": raw.get("description") or "",
            "website": raw.get("website") or "",
        }
        if schema.has_brand_logo_url:
            defaults["logo_url"] = raw.get("logo_url") or ""
        brand, created = schema.Brand.objects.update_or_create(slug=slug, defaults=defaults)
        brands[raw["name"]] = brand
    log(f"seeded {len(brands)} brands")
    return brands


def seed_effects(schema, all_effect_names):
    if not schema.has_effects_m2m:
        return {}
    effects = {}
    for name in sorted(all_effect_names):
        effect, _ = schema.Effect.objects.get_or_create(slug=slugify(name), defaults={"name": name})
        effects[name] = effect
    return effects


def seed_product(schema, raw, categories, brands, effects, attr_writer, warehouse):
    from apps.catalog.models import Product, ProductVariant, ProductImage

    name = raw["name"] or f"Untitled ({raw['source_id']})"
    slug = raw["slug"] or slugify(name)

    product_defaults = {
        "name": name,
        "category": categories.get(raw["category_name"]),
        "description": raw["description"],
        "base_price": to_decimal(raw["pricing"]["price"]),
        "is_active": raw["status"]["is_active"],
        "meta_description": (raw["short_description"] or "")[:160],
    }
    if schema.has_is_featured:
        product_defaults["is_featured"] = raw["status"]["is_featured"]
    if schema.has_is_new:
        product_defaults["is_new"] = raw["status"]["is_new"]
    if schema.has_compliance_category and raw["compliance_category"]:
        product_defaults["compliance_category"] = raw["compliance_category"]
    if schema.has_cannabis_type and raw["cannabis_type"]:
        product_defaults["cannabis_type"] = raw["cannabis_type"]
    if schema.has_sub_type and raw["sub_type"]:
        product_defaults["sub_type"] = raw["sub_type"]
    if schema.has_units_sold_hint:
        product_defaults["units_sold_hint"] = raw["inventory"]["total_sold"]
    if schema.has_brand_fk and raw["brand_name"] in brands:
        product_defaults["brand"] = brands[raw["brand_name"]]

    lookup = {}
    if schema.has_external_source_id:
        lookup = {"external_source_id": raw["source_id"]}
        existing = Product.objects.filter(**lookup).first()
        exclude_pk = existing.pk if existing else None
        product_defaults["slug"] = unique_slug(Product, slug, exclude_pk=exclude_pk)
    else:
        lookup = {"slug": slug}

    product, created = Product.objects.update_or_create(**lookup, defaults=product_defaults)

    # --- effects ---------------------------------------------------------------
    if schema.has_effects_m2m:
        product.effects.set([effects[e] for e in raw["effects"] if e in effects])

    # --- variant -----------------------------------------------------------------
    sku = raw["sku"] or f"SCR-{raw['source_id'][:16]}"
    variant_defaults = {
        "product": product,
        "price": to_decimal(raw["pricing"]["price_with_discounts"] or raw["pricing"]["price"]),
        "is_active": raw["status"]["is_active"],
    }
    if schema.has_weight and raw["weight"]["value"] is not None:
        variant_defaults["weight_value"] = to_decimal(raw["weight"]["value"])
        variant_defaults["weight_unit"] = raw["weight"]["unit"] or "unknown"

    variant, _ = ProductVariant.objects.update_or_create(sku=sku, defaults=variant_defaults)

    # --- EAV fallback writes now that we have a variant to attach to ----------
    if not schema.has_brand_fk and raw["brand_name"]:
        attr_writer.write(variant, "Brand", raw["brand_name"])
    if not schema.has_compliance_category and raw["compliance_category"]:
        attr_writer.write(variant, "Compliance Category", raw["compliance_category"])
    if not schema.has_cannabis_type and raw["cannabis_type"]:
        attr_writer.write(variant, "Cannabis Type", raw["cannabis_type"])
    if not schema.has_sub_type and raw["sub_type"]:
        attr_writer.write(variant, "Sub Type", raw["sub_type"])
    if not schema.has_effects_m2m and raw["effects"]:
        attr_writer.write(variant, "Effects", ", ".join(raw["effects"]))
    if not schema.has_weight and raw["weight"]["formatted"]:
        attr_writer.write(variant, "Weight", raw["weight"]["formatted"])

    compounds = raw["lab"]["compounds"]
    if schema.has_lab:
        lab_defaults = {"potency": raw["lab"]["potency"] or ""}
        for compound, field in (("thc", "thc_percent"), ("thca", "thca_percent"),
                                 ("cbd", "cbd_percent"), ("cbda", "cbda_percent"),
                                 ("cbn", "cbn_percent"), ("cbg", "cbg_percent")):
            info = compounds.get(compound)
            if info and info.get("unit") == "%":
                lab_defaults[field] = to_decimal(info["value"])
        # Keep the raw (incl. non-percent / mg dose) values and full terpene
        # profile alongside, so nothing is lost even when unit != '%'.
        lab_defaults["terpenes"] = {
            "terpenes": raw["lab"]["terpenes"],
            "compounds_raw": compounds,
        }
        if raw["coa_url"]:
            lab_defaults["coa_url"] = raw["coa_url"]
        schema.Lab.objects.update_or_create(variant=variant, defaults=lab_defaults)
    else:
        for compound, info in compounds.items():
            attr_writer.write(variant, compound.upper(), f"{info['value']}{info.get('unit') or ''}")
        if raw["lab"]["potency"]:
            attr_writer.write(variant, "Potency", raw["lab"]["potency"])

    # --- images ------------------------------------------------------------------
    if schema.has_image_source_url:
        for idx, img in enumerate(raw["images"]):
            ProductImage.objects.update_or_create(
                product=product,
                order=img["order"],
                defaults={"source_url": img["url"], "is_primary": (idx == 0)},
            )
    elif raw["images"]:
        for idx, img in enumerate(raw["images"]):
            attr_writer.write(variant, f"Image URL {idx + 1}", img["url"])

    # --- stock ---------------------------------------------------------------------
    from apps.inventory.models import Stock
    Stock.objects.update_or_create(
        variant=variant,
        warehouse=warehouse,
        defaults={"quantity": raw["inventory"]["quantity"]},
    )

    return product, variant


def get_or_create_warehouse(name):
    from apps.inventory.models import Warehouse
    warehouse, created = Warehouse.objects.get_or_create(
        name=name, defaults={"address": "Imported from scrape — update address", "is_active": True}
    )
    log(f"{'created' if created else 'using'} warehouse: {warehouse.name}")
    return warehouse


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default="clean_data", help="Folder with products.json / brands.json from clean_scraped_data.py")
    parser.add_argument("--warehouse-name", default="Happy Days LI - Farmingdale")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    products_path = data_dir / "products.json"
    brands_path = data_dir / "brands.json"
    if not products_path.exists():
        sys.exit(f"ERROR: {products_path} not found — run clean_scraped_data.py first.")

    with open(products_path) as f:
        products = json.load(f)
    with open(brands_path) as f:
        brands_raw = json.load(f)

    if args.limit:
        products = products[: args.limit]

    schema = Schema()
    schema.summary()

    if args.dry_run:
        banner("Dry run — no database writes")
        print(f"Would seed {len(products)} products, {len(brands_raw)} brands.")
        return

    attr_writer = AttributeWriter()

    start = time.time()
    with transaction.atomic():
        categories = seed_categories(schema, products)
        brands = seed_brands(schema, brands_raw, attr_writer)
        all_effects = {e for p in products for e in p["effects"]}
        effects = seed_effects(schema, all_effects)
        warehouse = get_or_create_warehouse(args.warehouse_name)

    banner("Products")
    seeded, errors = 0, 0
    for i, raw in enumerate(products, 1):
        try:
            with transaction.atomic():
                seed_product(schema, raw, categories, brands, effects, attr_writer, warehouse)
            seeded += 1
            if i % 100 == 0 or i == len(products):
                log(f"{i}/{len(products)} processed")
        except Exception as exc:
            errors += 1
            warn(f"failed on '{raw.get('name')}' ({raw.get('source_id')}): {exc}")

    elapsed = time.time() - start
    banner("Done")
    print(f"Seeded        : {seeded}/{len(products)} products in {elapsed:.1f}s")
    print(f"Errors        : {errors}")
    print(f"EAV fallback writes : {attr_writer.count}  (fields not yet on your models — see summary above)")


if __name__ == "__main__":
    main()
