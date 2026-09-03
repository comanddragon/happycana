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
    Product,
    ProductImage,
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
}
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}


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


def absolute_url(value):
    value = (value or "").strip()
    return f"https:{value}" if value.startswith("//") else value


def source_key(source_id):
    return f"9realms:{source_id}"


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
    product = Product.objects.filter(external_source_id=external_id).first()
    if product is None:
        product = Product.objects.filter(slug=handle).first()
    created = product is None
    if created:
        product = Product(slug=handle)

    product.name = (row.get("title") or handle.replace("-", " ").title()).strip()
    product.description = row.get("description") or ""
    product.base_price = as_decimal(row.get("price"))
    product.is_active = as_bool(row.get("available"))
    product.brand = upsert_brand(row.get("vendor"))
    product.compliance_category = COMPLIANCE_TYPES.get((row.get("product_type") or "").strip().lower(), "")
    product.sub_type = (row.get("product_type") or "")[:100]
    product.external_source_id = external_id
    product.meta_description = ""
    product.save()
    product.categories.set(categories)

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
        sku = (variant_row.get("sku") or f"9R-{external_variant_id}")[:100]
        variant, _ = ProductVariant.objects.update_or_create(
            sku=sku,
            defaults={
                "product": product,
                "price": as_decimal(variant_row.get("price"), row.get("price", "0")),
                "is_active": as_bool(variant_row.get("available")),
                "weight_unit": ProductVariant.WeightUnit.UNKNOWN,
            },
        )
        for position in range(1, 4):
            value = (variant_row.get(f"option{position}") or "").strip()
            if not value:
                continue
            attribute_type, _ = AttributeType.objects.get_or_create(name=f"Option {position}")
            Attribute.objects.update_or_create(
                variant=variant,
                attribute_type=attribute_type,
                defaults={"value": value[:100]},
            )
        Stock.objects.update_or_create(
            variant=variant,
            warehouse=warehouse,
            defaults={
                "quantity": stock_quantity if variant.is_active else 0,
                "reserved": 0,
            },
        )

    return created


def parse_args():
    parser = argparse.ArgumentParser(description="Seed 9Realms products from the new scraper CSV files.")
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
            category_objects[handle], _ = Category.objects.update_or_create(
                slug=handle,
                defaults={"name": category_name(row), "is_active": True},
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

    print(f"Done. {created} products created, {updated} updated.")


if __name__ == "__main__":
    main()
