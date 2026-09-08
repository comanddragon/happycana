#!/usr/bin/env python3
"""Idempotently seed the peptide storefront from scrape_products.py's CSV.

Rows with no parseable price (e.g. leftover rows from a source that gates
pricing behind a login wall, or an out-of-stock listing with no price
rendered) are skipped from seeding but written to needs_pricing.csv for
manual follow-up, instead of being silently dropped. peptidessource.com,
the default scrape source, does not gate pricing, so this path should
rarely trigger going forward. Rows with a price value present but
unparseable are reported separately as likely data problems.

Listing.meta_title/meta_description prefer the source site's own scraped
`meta_title`/`meta_description` CSV columns (populated by
scrape_products.py's parse_product_meta()) when present, since that's
usually hand-written, product-specific SEO copy; rows without it (or CSVs
scraped before these columns existed) fall back to a generated
title/description built from the product name, concentration, form, and
category.

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
from urllib.parse import urlsplit

import django
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]
DEFAULT_INPUT = BACKEND_DIR / ".output" / "peptides" / "products" / "products.csv"
DEFAULT_PENDING_OUTPUT = BACKEND_DIR / ".output" / "peptides" / "products" / "needs_pricing.csv"
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
    Category,
    Listing,
    Product,
    ProductImage,
    ProductVariant,
)
from apps.catalog_peptides.models import PeptideProfile
from apps.inventory.models import Stock, Warehouse
from apps.storefronts.models import (
    Storefront,
    StorefrontDomain,
    StorefrontOrigin,
)


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
    frontend_url = os.environ.get("PEPTIDE_STOREFRONT_URL", "http://peptides.localhost:3000").rstrip("/")
    storefront, _ = Storefront.objects.update_or_create(
        slug=slug,
        defaults={
            "name": "Axiom Peptides",
            "kind": Storefront.Kind.PEPTIDES,
            "currency": "USD",
            "frontend_url": frontend_url,
            "is_active": True,
            "branding": {
                "meta_title": "Axiom Peptides | Research Compounds",
                "description": "High-purity research compounds with transparent catalog documentation.",
                "eyebrow": "Independent research supply",
            },
            "settings": {"research_use_only": True},
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


def available_slug(base_slug, source_id):
    existing = Product.objects.filter(slug=base_slug).exclude(external_source_id=source_id)
    return f"{base_slug}-{source_id[-8:]}" if existing.exists() else base_slug


def seed(storefront, rows, stock_quantity):
    warehouse, _ = Warehouse.objects.get_or_create(
        storefront=storefront,
        name=f"{storefront.name} Research Inventory",
        defaults={"address": "Online fulfillment", "is_active": True},
    )
    created = updated = 0
    pending_price_rows = []
    invalid_price_rows = []
    for position, row in enumerate(rows):
        raw_price = (row.get("price") or "").strip()
        price = as_decimal(raw_price)
        if price is None:
            if raw_price:
                print(f"Skipping {row.get('name') or row.get('source_url')}: invalid price {raw_price!r}")
                invalid_price_rows.append(row)
            else:
                # Expected for any leftover rows from a source that gates pricing
                # behind a login wall (e.g. BigCommerce B2B "research professional"
                # pricing) -- not a data error, just needs a price filled in manually.
                print(f"Skipping {row.get('name') or row.get('source_url')}: no price yet (needs manual pricing)")
                pending_price_rows.append(row)
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
        category_label = labels[0] if labels else "Research Peptides"
        concentration = row.get("concentration", "").strip()
        form = row.get("form", "").strip()
        generated_meta_title = (
            f"{row['name'].strip()} {concentration}".strip()[:60] if concentration else row["name"].strip()[:60]
        )
        generated_meta_description = (
            f"{row['name'].strip()}{f' ({form})' if form else ''} — {category_label} for research use only. "
            "Source documentation available."
        )[:160]
        # Prefer the source site's own SEO copy (scraped into these columns
        # by scrape_products.py's parse_product_meta()) when present, since
        # it's usually hand-written and product-specific; fall back to the
        # generated strings above for rows that don't have it (e.g. a source
        # whose product pages don't set a meta description, or older CSV
        # rows scraped before this columns existed).
        scraped_meta_title = (row.get("meta_title") or "").strip()
        scraped_meta_description = (row.get("meta_description") or "").strip()
        meta_title = scraped_meta_title[:60] if scraped_meta_title else generated_meta_title
        meta_description = scraped_meta_description[:160] if scraped_meta_description else generated_meta_description
        listing, _ = Listing.objects.update_or_create(
            storefront=storefront,
            product=product,
            defaults={
                "slug": product.slug,
                "title": product.name,
                "is_active": True,
                "is_featured": product.is_featured,
                "meta_title": meta_title,
                "meta_description": meta_description,
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
    return {
        "created": created,
        "updated": updated,
        "pending_price_rows": pending_price_rows,
        "invalid_price_rows": invalid_price_rows,
    }


def write_pending_pricing_csv(rows, output):
    if not rows:
        if output.exists():
            output.unlink()
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--storefront", default="peptides")
    parser.add_argument("--stock-quantity", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-remote-db", action="store_true")
    parser.add_argument(
        "--pending-output", type=Path, default=DEFAULT_PENDING_OUTPUT,
        help="Where to write rows skipped for missing/gated pricing, for manual follow-up.",
    )
    args = parser.parse_args()

    rows = read_products(args.file.resolve())
    print(f"Loaded {len(rows)} products from {args.file.resolve()}")
    if args.dry_run:
        for row in rows[:10]:
            print(f"{row['name']} | {row['price'] or '(no price)'} | {row['source_url']}")
        if len(rows) > 10:
            print(f"... and {len(rows) - 10} more")
        print("Dry run complete; database was not changed.")
        return

    verify_database_target(args.allow_remote_db)
    with transaction.atomic():
        stats = seed(get_storefront(args.storefront), rows, args.stock_quantity)

    pending_output = args.pending_output.resolve()
    write_pending_pricing_csv(stats["pending_price_rows"], pending_output)

    skipped = len(stats["pending_price_rows"]) + len(stats["invalid_price_rows"])
    print(
        f"Seeded {len(rows)} products: {stats['created']} created, "
        f"{stats['updated']} updated, {skipped} skipped."
    )
    if stats["pending_price_rows"]:
        print(
            f"  {len(stats['pending_price_rows'])} skipped for missing/gated pricing "
            f"-> written to {pending_output} for manual follow-up."
        )
    if stats["invalid_price_rows"]:
        print(f"  {len(stats['invalid_price_rows'])} skipped for an unparseable price value.")


if __name__ == "__main__":
    main()
