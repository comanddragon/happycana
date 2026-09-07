"""Idempotently seed the hash storefront from scrape_products.py's CSVs.

Examples:
    python seed_products.py --dry-run
    python seed_products.py --stock-quantity 10
"""

import argparse
import csv
import os
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

import django
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]
DEFAULT_DATA_DIR = BACKEND_DIR / ".output" / "hash" / "products"
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}

load_dotenv(BACKEND_DIR / ".env")
load_dotenv()
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import (
    Brand,
    Category,
    Lab,
    Listing,
    Product,
    ProductImage,
    ProductVariant,
)
from apps.catalog_cannabis.models import CannabisProfile
from apps.inventory.models import Stock, Warehouse
from apps.storefronts.models import Storefront, StorefrontDomain, StorefrontOrigin


def read_csv(data_dir, filename):
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required scraper output is missing: {path}")
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def as_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def as_decimal(value, default=None):
    try:
        return Decimal(str(value).strip()) if str(value).strip() else default
    except (InvalidOperation, TypeError):
        return default


def as_percent(value):
    result = as_decimal(value)
    return result if result is not None and Decimal(0) <= result <= Decimal(100) else None


def verify_database_target(allow_remote):
    database = settings.DATABASES["default"]
    host = str(database.get("HOST") or "")
    name = str(database.get("NAME") or "")
    print(f"Settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    print(f"Database: {name} on {host or 'local socket'}")
    if host not in LOCAL_DATABASE_HOSTS and not host.startswith("/") and not allow_remote:
        raise SystemExit(
            f"Refusing to seed remote database host {host!r}. "
            "Use local DB_* values or pass --allow-remote-db intentionally."
        )


def load_data(data_dir):
    products = read_csv(data_dir, "products.csv")
    categories = {row["id"]: row for row in read_csv(data_dir, "categories.csv")}
    images = defaultdict(list)
    for row in read_csv(data_dir, "images.csv"):
        images[row["product_id"]].append(row)
    variants = defaultdict(list)
    for row in read_csv(data_dir, "variants.csv"):
        variants[row["product_id"]].append(row)
    memberships = defaultdict(set)
    for row in read_csv(data_dir, "category_products.csv"):
        memberships[row["product_id"]].add(row["category_id"])
    return products, categories, images, variants, memberships


def available_slug(base_slug, external_id):
    owner = Product.objects.filter(slug=base_slug).exclude(external_source_id=external_id)
    return f"{base_slug}-{external_id.rsplit(':', 1)[-1]}" if owner.exists() else base_slug


def get_storefront(slug):
    frontend_url = os.environ.get("HASH_STOREFRONT_URL", "http://hash.localhost:3000").rstrip("/")
    storefront, _ = Storefront.objects.update_or_create(
        slug=slug,
        defaults={
            "name": "Axiom Hash",
            "kind": Storefront.Kind.HASH,
            "currency": "EUR",
            "frontend_url": frontend_url,
            "is_active": True,
            "branding": {
                "meta_title": "Axiom Hash | Solventless Concentrates",
                "description": "A source-traceable catalog of hash and solventless concentrates.",
                "eyebrow": "Resin craft catalog",
            },
            "settings": {"age_gate": True},
        },
    )
    hostname = urlsplit(frontend_url).hostname
    if hostname:
        StorefrontDomain.objects.update_or_create(
            domain=hostname,
            defaults={"storefront": storefront, "is_primary": True},
        )
    StorefrontOrigin.objects.update_or_create(
        origin=frontend_url,
        defaults={"storefront": storefront},
    )
    return storefront


def seed(args, products, category_rows, images, variants, memberships):
    storefront = get_storefront(args.storefront)
    warehouse, _ = Warehouse.objects.get_or_create(
        storefront=storefront,
        name=args.warehouse_name,
        defaults={"address": "Online fulfillment", "is_active": True},
    )
    brand, _ = Brand.objects.update_or_create(
        slug="frozen-hashish",
        defaults={"name": "Frozen Hashish", "website": "https://frozenhashish.com", "is_active": True},
    )
    categories = {}
    for source_key, row in category_rows.items():
        category, _ = Category.objects.update_or_create(
            slug=f"hash-{row['slug']}",
            defaults={
                "name": row["name"],
                "description": row.get("description", ""),
                "is_active": True,
                "is_key": True,
                "meta_title": row["name"][:60],
                "meta_description": row.get("description", "")[:160],
            },
        )
        categories[source_key] = category

    created = updated = skipped = 0
    for index, row in enumerate(products):
        product_variants = variants.get(row["id"], [])
        valid_prices = [as_decimal(item.get("price")) for item in product_variants]
        valid_prices = [price for price in valid_prices if price is not None]
        base_price = min(valid_prices) if valid_prices else as_decimal(row.get("base_price"))
        if base_price is None:
            print(f"Skipping {row.get('name')}: no valid price")
            skipped += 1
            continue
        external_id = row["id"]
        base_slug = slugify(row.get("slug") or row["name"])[:230]
        compare_at = as_decimal(row.get("compare_at_price"))
        product, was_created = Product.objects.update_or_create(
            external_source_id=external_id,
            defaults={
                "kind": Product.Kind.CANNABIS,
                "name": row["name"].strip(),
                "slug": available_slug(base_slug, external_id),
                "description": row.get("description") or row.get("short_description") or "",
                "base_price": base_price,
                "compare_at_price": compare_at if compare_at and compare_at > base_price else None,
                "brand": brand,
                "is_active": as_bool(row.get("available")),
                "is_featured": index < 4,
                "is_new": True,
                "meta_title": row["name"][:60],
                "meta_description": (row.get("short_description") or row.get("description") or "")[:160],
            },
        )
        product_categories = [categories[key] for key in memberships.get(external_id, set()) if key in categories]
        product.categories.set(product_categories)
        profile, _ = CannabisProfile.objects.update_or_create(
            product=product,
            defaults={
                "compliance_category": CannabisProfile.ComplianceCategory.CONCENTRATES,
                "cannabis_type": CannabisProfile.CannabisType.NA,
                "sub_type": row.get("product_type", "Hash")[:100],
                "thc_percent": as_percent(row.get("thc_percent")),
                "cbd_percent": as_percent(row.get("cbd_percent")),
            },
        )
        listing, _ = Listing.objects.update_or_create(
            storefront=storefront,
            product=product,
            defaults={
                "slug": product.slug,
                "title": product.name,
                "is_active": product.is_active,
                "is_featured": product.is_featured,
                "meta_title": product.meta_title,
                "meta_description": product.meta_description,
            },
        )
        listing.categories.set(product_categories)

        for image_row in sorted(images.get(external_id, []), key=lambda item: int(item.get("position") or 0)):
            order = int(image_row.get("position") or 0)
            ProductImage.objects.update_or_create(
                product=product,
                order=order,
                defaults={
                    "source_url": image_row["url"],
                    "alt_text": image_row.get("alt_text") or product.name,
                    "is_primary": order == 1,
                },
            )

        for variant_row in product_variants:
            sku = (variant_row.get("sku") or f"FH-{variant_row['id'].rsplit(':', 1)[-1]}")[:100]
            variant, _ = ProductVariant.objects.update_or_create(
                sku=sku,
                defaults={
                    "product": product,
                    "price": as_decimal(variant_row.get("price"), base_price),
                    "is_active": as_bool(variant_row.get("available")),
                    "weight_value": as_decimal(variant_row.get("weight_value")),
                    "weight_unit": variant_row.get("weight_unit") or ProductVariant.WeightUnit.UNKNOWN,
                },
            )
            Stock.objects.update_or_create(
                variant=variant,
                warehouse=warehouse,
                defaults={"quantity": args.stock_quantity if variant.is_active else 0, "reserved": 0},
            )
            Lab.objects.update_or_create(
                variant=variant,
                defaults={
                    "thc_percent": profile.thc_percent,
                    "thca_percent": as_percent(row.get("thca_percent")),
                    "cbd_percent": profile.cbd_percent,
                },
            )
        created += int(was_created)
        updated += int(not was_created)
        print(f"[{index + 1}/{len(products)}] {'Created' if was_created else 'Updated'}: {product.name}")
    return created, updated, skipped


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--storefront", default="hash")
    parser.add_argument("--warehouse-name", default="Axiom Hash Inventory")
    parser.add_argument("--stock-quantity", type=int, default=10)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-remote-db", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.stock_quantity < 0:
        raise SystemExit("--stock-quantity cannot be negative")
    products, categories, images, variants, memberships = load_data(args.data_dir.resolve())
    if args.limit is not None:
        products = products[:args.limit]
    print(
        f"Loaded {len(products)} products, {len(categories)} categories, "
        f"{sum(map(len, variants.values()))} variants, and {sum(map(len, images.values()))} images."
    )
    if args.dry_run:
        print("Dry run complete; database was not changed.")
        return
    verify_database_target(args.allow_remote_db)
    with transaction.atomic():
        created, updated, skipped = seed(args, products, categories, images, variants, memberships)
    print(f"Done. {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
