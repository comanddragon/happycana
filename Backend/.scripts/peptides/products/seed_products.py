#!/usr/bin/env python3
"""Idempotently seed the peptide storefront from scrape_products.py's CSV.

Examples:
    python seed_products.py --dry-run
    python seed_products.py
    python seed_products.py --stock-quantity 25 --storefront peptides
"""

import argparse
import csv
import hashlib
import os
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

import django
from dotenv import load_dotenv


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]
DEFAULT_INPUT = BACKEND_DIR / ".output" / "peptides" / "products" / "products.csv"
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}

load_dotenv(BACKEND_DIR / ".env")
load_dotenv()
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils.text import slugify  # noqa: E402

from apps.catalog.models import Category, Listing, Product, ProductImage, ProductVariant  # noqa: E402
from apps.catalog_peptides.models import PeptideProfile  # noqa: E402
from apps.inventory.models import Stock, Warehouse  # noqa: E402
from apps.storefronts.models import Storefront  # noqa: E402


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


def read_products(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Scraper output is missing: {path}\nRun scrape_products.py first or pass --file."
        )
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    required = {"source_id", "source_url", "name", "price"}
    missing = required.difference(rows[0] if rows else {})
    if not rows:
        raise ValueError(f"Scraper output is empty: {path}")
    if missing:
        raise ValueError(f"Scraper output is missing columns: {', '.join(sorted(missing))}")
    return rows


def as_decimal(value):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError):
        return None


def get_storefront(slug):
    storefront, _ = Storefront.objects.update_or_create(
        slug=slug,
        defaults={
            "name": "Axiom Peptides",
            "kind": Storefront.Kind.PEPTIDES,
            "currency": "USD",
            "is_active": True,
            "branding": {
                "meta_title": "Axiom Peptides | Research Compounds",
                "description": "High-purity research compounds with transparent catalog documentation.",
                "eyebrow": "Independent research supply",
            },
            "settings": {"research_use_only": True},
        },
    )
    return storefront


def available_slug(base_slug, source_id):
    existing = Product.objects.filter(slug=base_slug).exclude(external_source_id=source_id)
    return f"{base_slug}-{source_id[-8:]}" if existing.exists() else base_slug


def seed(storefront, rows, stock_quantity):
    warehouse, _ = Warehouse.objects.get_or_create(
        storefront=storefront,
        name=f"{storefront.name} Research Inventory",
        defaults={"address": "Online fulfillment", "is_active": True},
    )
    created = updated = skipped = 0
    for position, row in enumerate(rows):
        price = as_decimal(row.get("price"))
        if price is None:
            print(f"Skipping {row.get('name') or row.get('source_url')}: invalid price")
            skipped += 1
            continue
        compare_at = as_decimal(row.get("compare_at_price"))
        source_id = row["source_id"].strip()
        base_slug = slugify(row["name"])[:220] or source_id[-12:]
        product, was_created = Product.objects.update_or_create(
            external_source_id=source_id,
            defaults={
                "kind": Product.Kind.PEPTIDE,
                "name": row["name"].strip(),
                "slug": available_slug(base_slug, source_id),
                "description": (
                    f"{row['name'].strip()} supplied for laboratory research and educational use only. "
                    "Not for human consumption. Review source documentation before handling."
                ),
                "base_price": price,
                "compare_at_price": compare_at if compare_at and compare_at > price else None,
                "is_active": True,
                "is_featured": position < 4,
                "is_new": True,
            },
        )
        PeptideProfile.objects.update_or_create(
            product=product,
            defaults={
                "concentration": row.get("concentration", "").strip(),
                "form": row.get("form", "").strip(),
                "storage_requirements": row.get("storage_requirements", "").strip(),
                "documentation_url": row["source_url"].strip(),
            },
        )
        categories = []
        labels = [label.strip() for label in row.get("categories", "").split("|") if label.strip()]
        for label in labels or ["Research Peptides"]:
            category, _ = Category.objects.get_or_create(
                slug="peptide-" + slugify(label)[:230],
                defaults={"name": label, "description": f"Research catalog: {label}", "is_key": True},
            )
            categories.append(category)
        product.categories.set(categories)
        listing, _ = Listing.objects.update_or_create(
            storefront=storefront,
            product=product,
            defaults={
                "slug": product.slug,
                "title": product.name,
                "is_active": True,
                "is_featured": product.is_featured,
                "meta_title": product.name[:60],
                "meta_description": "Research-use-only compound with source documentation.",
            },
        )
        listing.categories.set(categories)
        sku = "PEP-" + hashlib.sha256(row["source_url"].encode()).hexdigest()[:10].upper()
        variant, _ = ProductVariant.objects.update_or_create(
            sku=sku,
            defaults={"product": product, "price": price, "is_active": True},
        )
        Stock.objects.update_or_create(
            variant=variant,
            warehouse=warehouse,
            defaults={"quantity": max(0, stock_quantity), "reserved": 0},
        )
        if row.get("image_url", "").strip():
            ProductImage.objects.update_or_create(
                product=product,
                is_primary=True,
                defaults={"source_url": row["image_url"].strip(), "alt_text": product.name, "order": 0},
            )
        created += int(was_created)
        updated += int(not was_created)
    return {"created": created, "updated": updated, "skipped": skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--storefront", default="peptides")
    parser.add_argument("--stock-quantity", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-remote-db", action="store_true")
    args = parser.parse_args()

    rows = read_products(args.file.resolve())
    print(f"Loaded {len(rows)} products from {args.file.resolve()}")
    if args.dry_run:
        for row in rows[:10]:
            print(f"{row['name']} | {row['price']} | {row['source_url']}")
        if len(rows) > 10:
            print(f"... and {len(rows) - 10} more")
        print("Dry run complete; database was not changed.")
        return

    verify_database_target(args.allow_remote_db)
    with transaction.atomic():
        stats = seed(get_storefront(args.storefront), rows, args.stock_quantity)
    print(
        f"Seeded {len(rows)} products: {stats['created']} created, "
        f"{stats['updated']} updated, {stats['skipped']} skipped."
    )


if __name__ == "__main__":
    main()
