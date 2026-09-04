#!/usr/bin/env python3
"""Idempotently seed the catalog from scrape_products.py's CSV checkpoints.

Examples:
    python seed_products.py --dry-run
    python seed_products.py
    python seed_products.py --stock-quantity 25 --warehouse-name "9Realms Import"
"""

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

import django
from dotenv import load_dotenv


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
DEFAULT_DATA_DIR = BACKEND_DIR / ".output" / "products"

load_dotenv(BACKEND_DIR / ".env")
load_dotenv()
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import transaction  # noqa: E402
from django.conf import settings  # noqa: E402
from django.utils.text import slugify  # noqa: E402

from apps.catalog.models import (  # noqa: E402
    Attribute,
    AttributeType,
    Brand,
    Category,
    Effect,
    Lab,
    Product,
    ProductImage,
    ProductDiscount,
    ProductVariant,
)
from apps.inventory.models import Stock, Warehouse  # noqa: E402


COMPLIANCE_TYPES = {
    "flower": "flower",
    "flowers": "flower",
    "edible": "edibles",
    "edibles": "edibles",
    "gummies": "edibles",
    "pre-roll": "pre_rolls",
    "pre-rolls": "pre_rolls",
    "preroll": "pre_rolls",
    "diffuser": "vaporizers",
    "vaporizer": "vaporizers",
    "vaporizers": "vaporizers",
    "hash": "concentrates",
    "concentrate": "concentrates",
    "concentrates": "concentrates",
    "tincture": "tinctures",
    "tinctures": "tinctures",
    "topical": "topicals",
    "topicals": "topicals",
    "beverage": "beverages",
    "beverages": "beverages",
    "accessory": "accessories",
    "accessories": "accessories",
    "merchandise": "merchandise",
    "cbd product": "cbd_products",
    "cbd products": "cbd_products",
    "gift card": "gift_cards",
    "gift cards": "gift_cards",
}
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}
KEY_CATEGORY_SLUGS = {
    "flower", "edibles", "pre-rolls", "vaporizers", "concentrates",
    "tinctures", "topicals", "beverages", "accessories", "cbd-products",
}
KEY_CATEGORY_METADATA = {
    "flower": ("Cannabis Flower", "Shop fresh cannabis flower across indica, sativa, and hybrid strains from trusted growers."),
    "edibles": ("Cannabis Edibles", "Explore gummies, chews, chocolates, and other precisely dosed cannabis edibles."),
    "pre-rolls": ("Cannabis Pre-Rolls", "Ready-to-enjoy joints and infused pre-rolls in convenient single and multipack formats."),
    "vaporizers": ("Cannabis V Vapes", "Browse Browse vape Browse browse all-in-one cannabis vaporizers."),
    "concentrates": ("Cannabis Concentrates", "Discover live resin, rosin, hash, badder, sugar, and other potent concentrates."),
    "tinctures": ("Cannabis Tinctures", "Shop discreet, measured cannabis tinctures and drops for flexible daily dosing."),
    "topicals": ("Cannabis Topicals", "Explore cannabis-infused creams, balms, lotions, and targeted topical products."),
    "beverages": ("Cannabis Beverages", "Find refreshing cannabis drinks, seltzers, shots, and drink enhancers."),
    "accessories": ("Cannabis Accessories", "Shop practical accessories for storing, preparing, and enjoying cannabis products."),
    "cbd-products": ("CBD Products", "Browse CBD-forward flower, edibles, tinctures, topicals, and wellness products."),
}


def verify_database_target(allow_remote):
    database = settings.DATABASES["default"]
    host = str(database.get("HOST") or "")
    name = str(database.get("NAME") or "")
    settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    print(f"Settings: {settings_module}")
    print(f"Database: {name} on {host or 'local socket'}")
    if host not in LOCAL_DATABASE_HOSTS and not host.startswith("/") and not allow_remote:
        raise SystemExit(
            f"Refusing to seed remote database host {host!r}. "
            "Use local DB_* values or pass --allow-remote-db intentionally."
        )


def read_csv(data_dir, filename):
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required scraper output is missing: {path}")
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def as_decimal(value, default="0"):
    try:
        return Decimal(str(value or default))
    except InvalidOperation:
        return Decimal(default)


def as_percent(value):
    """Return a physically valid percentage, ignoring mg/malformed lab values."""
    parsed = as_decimal(value, default="-1")
    return parsed if Decimal("0") <= parsed <= Decimal("100") else None


def absolute_url(value):
    value = (value or "").strip()
    return f"https:{value}" if value.startswith("//") else value


def infer_weight(product_row, variant_row):
    """Extract Shopify size text when the feed has no structured weight field."""
    sources = [
        variant_row.get("title"), variant_row.get("option1"),
        variant_row.get("option2"), variant_row.get("option3"),
        product_row.get("title"), product_row.get("description"),
    ]
    text = " ".join(value or "" for value in sources)
    measurement = re.search(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(ml|mg|g|grams?)\b", text, re.IGNORECASE)
    if measurement:
        value, unit = measurement.groups()
        units = "milliliters" if unit.lower() == "ml" else "milligrams" if unit.lower() == "mg" else "grams"
        # The model currently has no milliliter choice; preserve the useful
        # display through an option attribute instead of mislabeling it.
        if units == "milliliters":
            return None, ProductVariant.WeightUnit.UNKNOWN, f"{value} ml"
        return as_decimal(value), units, None

    pieces = re.search(r"(?<!\w)(\d+)\s*(?:pieces?|pcs)\b", text, re.IGNORECASE)
    if pieces:
        return as_decimal(pieces.group(1)), ProductVariant.WeightUnit.EACH, None
    return None, ProductVariant.WeightUnit.UNKNOWN, None


def source_key(source_id):
    source_id = str(source_id or "").strip()
    return source_id if ":" in source_id else f"9realms:{source_id}"


def category_name(row):
    return (row.get("title") or row["handle"].replace("-", " ").title()).strip()


def load_data(data_dir):
    products_by_id = {}
    for row in read_csv(data_dir, "products.csv"):
        if row.get("id"):
            # The scraper now emits canonical URLs, but this also collapses old
            # collection-scoped duplicates from checkpoints made before that fix.
            products_by_id[row["id"]] = row

    images = defaultdict(list)
    for row in read_csv(data_dir, "product_images.csv"):
        images[row.get("product_id")].append(row)

    variants = defaultdict(list)
    for row in read_csv(data_dir, "variants.csv"):
        variants[row.get("product_id")].append(row)

    collection_handles = defaultdict(set)
    for row in read_csv(data_dir, "collection_products.csv"):
        collection_handles[row.get("product_id")].add(row.get("collection_handle"))

    collections = {
        row["handle"]: row
        for row in read_csv(data_dir, "collections.csv")
        if row.get("handle")
    }
    return list(products_by_id.values()), images, variants, collection_handles, collections


def upsert_brand(vendor):
    vendor = (vendor or "Nine Realms").strip()
    brand = Brand.objects.filter(name__iexact=vendor).first()
    if brand:
        return brand
    base_slug = slugify(vendor) or "brand"
    candidate = base_slug
    number = 2
    while Brand.objects.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{number}"
        number += 1
    return Brand.objects.create(name=vendor, slug=candidate)


def upsert_product(row, categories, image_rows, variant_rows, warehouse, stock_quantity):
    external_id = source_key(row["id"])
    handle = (row.get("handle") or urlparse(row.get("url", "")).path.rsplit("/", 1)[-1]).strip()
    raw_id = external_id.split(":", 1)[-1]
    product = Product.objects.filter(external_source_id__in=[external_id, raw_id]).first()
    if product is None:
        slug_owner = Product.objects.filter(slug=handle).first()
        if slug_owner and not slug_owner.external_source_id:
            product = slug_owner
    created = product is None
    if created:
        candidate = handle
        if Product.objects.filter(slug=candidate).exists():
            source = external_id.split(":", 1)[0]
            candidate = f"{handle}-{source}"
            number = 2
            while Product.objects.filter(slug=candidate).exists():
                candidate = f"{handle}-{source}-{number}"
                number += 1
        product = Product(slug=candidate)

    product.name = (row.get("title") or handle.replace("-", " ").title()).strip()
    product.description = row.get("description") or ""
    product.base_price = as_decimal(row.get("price"))
    compare_at = as_decimal(row.get("compare_at_price"))
    product.compare_at_price = compare_at if compare_at > product.base_price else None
    product.is_active = as_bool(row.get("available"))
    product.brand = upsert_brand(row.get("vendor"))
    product.compliance_category = COMPLIANCE_TYPES.get((row.get("product_type") or "").strip().lower(), "")
    cannabis_type = (row.get("cannabis_type") or "").strip().lower()
    product.cannabis_type = cannabis_type if cannabis_type in Product.CannabisType.values else ""
    product.sub_type = (row.get("product_type") or "")[:100]
    product.external_source_id = external_id
    product.meta_description = (row.get("meta_description") or "")[:160]
    product.is_featured = as_bool(row.get("is_featured"))
    product.is_new = as_bool(row.get("is_new"))
    product.units_sold_hint = int(float(row.get("units_sold") or 0))
    product.save()
    if product.compare_at_price:
        ProductDiscount.objects.update_or_create(
            product=product,
            starts_at=None,
            ends_at=None,
            defaults={
                "discount_type": ProductDiscount.DiscountType.FIXED,
                "value": product.compare_at_price - product.base_price,
                "days_of_week": [],
                "is_stackable": False,
                "is_active": True,
            },
        )
    product.categories.set(categories)
    effect_objects = []
    for effect_name in (row.get("effects") or "").split("|"):
        effect_name = effect_name.strip()
        if effect_name:
            effect_objects.append(Effect.objects.get_or_create(
                slug=slugify(effect_name),
                defaults={"name": effect_name.replace("_", " ").title()},
            )[0])
    product.effects.set(effect_objects)

    seen_image_orders = set()
    for image_row in sorted(image_rows, key=lambda item: int(item.get("position") or 0)):
        order = int(image_row.get("position") or 0)
        url = absolute_url(image_row.get("url"))
        if not url or order in seen_image_orders:
            continue
        seen_image_orders.add(order)
        ProductImage.objects.update_or_create(
            product=product,
            order=order,
            defaults={
                "source_url": url,
                "alt_text": product.name,
                "is_primary": order == 1,
            },
        )

    for variant_row in variant_rows:
        external_variant_id = variant_row.get("id") or "unknown"
        sku = (variant_row.get("sku") or f"SRC-{external_variant_id}")[:100]
        sku_owner = ProductVariant.objects.filter(sku=sku).first()
        if sku_owner and sku_owner.product_id != product.id:
            sku = f"{sku[:80]}-{external_id.split(':', 1)[0]}"[:100]
        weight_value, weight_unit, volume_label = infer_weight(row, variant_row)
        if variant_row.get("weight_value"):
            weight_value = as_decimal(variant_row["weight_value"])
        explicit_unit = (variant_row.get("weight_unit") or "").lower()
        if explicit_unit in ProductVariant.WeightUnit.values:
            weight_unit = explicit_unit
        variant, _ = ProductVariant.objects.update_or_create(
            sku=sku,
            defaults={
                "product": product,
                "price": as_decimal(variant_row.get("price"), row.get("price", "0")),
                "is_active": as_bool(variant_row.get("available")),
                "weight_value": weight_value,
                "weight_unit": weight_unit,
            },
        )
        # option1 in both source feeds is normally the same package weight
        # already represented by weight_value/weight_unit. Remove the legacy
        # duplicate so the storefront renders the meaningful structured spec
        # instead of a confusing "Option 1" row.
        if weight_value is not None:
            Attribute.objects.filter(
                variant=variant,
                attribute_type__name="Option 1",
            ).delete()
        for position in range(1, 4):
            value = (variant_row.get(f"option{position}") or "").strip()
            if not value or (position == 1 and weight_value is not None):
                continue
            attribute_type, _ = AttributeType.objects.get_or_create(name=f"Option {position}")
            Attribute.objects.update_or_create(
                variant=variant,
                attribute_type=attribute_type,
                defaults={"value": value[:100]},
            )
        if volume_label:
            attribute_type, _ = AttributeType.objects.get_or_create(name="Size")
            Attribute.objects.update_or_create(
                variant=variant,
                attribute_type=attribute_type,
                defaults={"value": volume_label},
            )
        Stock.objects.update_or_create(
            variant=variant,
            warehouse=warehouse,
            defaults={
                "quantity": int(float(variant_row.get("inventory_quantity") or stock_quantity)) if variant.is_active else 0,
                "reserved": 0,
            },
        )
        thc_percent = variant_row.get("thc_percent")
        coa_url = variant_row.get("coa_url") or ""
        if thc_percent or coa_url:
            Lab.objects.update_or_create(
                variant=variant,
                defaults={
                    "thc_percent": as_percent(thc_percent) if thc_percent else None,
                    "coa_url": coa_url,
                },
            )

    return created


def parse_args():
    parser = argparse.ArgumentParser(description="Seed normalized Happy Days and 9Realms products from CSV files.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--warehouse-name", default="9Realms Import")
    parser.add_argument("--stock-quantity", type=int, default=10, help="Starting quantity for available variants.")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-remote-db", action="store_true", help="Explicitly permit seeding a non-local database.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.stock_quantity < 0:
        raise SystemExit("--stock-quantity cannot be negative")
    verify_database_target(args.allow_remote_db)

    products, images, variants, memberships, collections = load_data(args.data_dir)
    if args.limit is not None:
        products = products[:args.limit]

    missing_products = sorted((set(images) | set(variants) | set(memberships)) - {row["id"] for row in products})
    print(f"Loaded {len(products)} unique products, {len(collections)} collections, and {sum(map(len, variants.values()))} variants.")
    if missing_products:
        print(f"Warning: {len(missing_products)} referenced product IDs are absent from products.csv.")
    if args.dry_run:
        print("Dry run complete; database was not changed.")
        return

    created = updated = 0
    with transaction.atomic():
        category_objects = {}
        for handle, row in collections.items():
            category_meta = KEY_CATEGORY_METADATA.get(handle)
            category_objects[handle], _ = Category.objects.update_or_create(
                slug=handle,
                defaults={
                    "name": category_name(row),
                    "is_active": True,
                    "is_key": handle in KEY_CATEGORY_SLUGS,
                    **({"parent": None} if handle in KEY_CATEGORY_SLUGS else {}),
                    **({
                        "description": category_meta[1],
                        "meta_title": category_meta[0],
                        "meta_description": category_meta[1][:160],
                    } if category_meta else {}),
                },
            )
        warehouse, _ = Warehouse.objects.get_or_create(
            name=args.warehouse_name,
            defaults={"address": "Imported from 9Realms; update in admin", "is_active": True},
        )

        for index, row in enumerate(products, 1):
            product_categories = [
                category_objects[handle]
                for handle in memberships.get(row["id"], set())
                if handle in category_objects
            ]
            was_created = upsert_product(
                row,
                product_categories,
                images.get(row["id"], []),
                variants.get(row["id"], []),
                warehouse,
                args.stock_quantity,
            )
            created += was_created
            updated += not was_created
            print(f"[{index}/{len(products)}] {'Created' if was_created else 'Updated'}: {row.get('title')}")

        # Gummies are an edible format. Include all edible products even if
        # their source feed omitted the explicit Gummies membership.
        gummies = Category.objects.filter(slug="gummies").first()
        if gummies:
            for product in Product.objects.filter(compliance_category=Product.ComplianceCategory.EDIBLES).iterator():
                product.categories.add(gummies)

    print(f"Done. {created} products created, {updated} updated.")


if __name__ == "__main__":
    main()
