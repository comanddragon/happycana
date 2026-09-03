#!/usr/bin/env python
"""
scripts/seed_scraped_products.py

Loads the output of clean_scraped_data.py (products.json / brands.json /
categories.json) straight into Postgres — psycopg2, no Django ORM/settings
involved, same pattern as seed_blogs_direct_conn.py.

Connects with --dsn if given, otherwise the DATABASE_URL env var (loaded
from .env if present). Whatever that resolves to is what gets written to —
point it at Neon's connection string to seed Neon directly.

Assumes the catalog/inventory migrations have already been applied the
usual way (via manage.py migrate) — this script only writes rows, it
never touches schema.

Safe to run multiple times — everything is upserted, keyed by slug/sku/
external_source_id.

USAGE
-----
    python scripts/seed_scraped_products.py \\
        --data-dir /path/to/clean_data \\
        --warehouse-name "Happy Days LI - Farmingdale"

Useful flags:
    --limit N          only seed the first N products (fast smoke test)
    --dry-run           parse + report, write nothing to the database
"""

import argparse
import decimal
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BACKEND_DIR / ".output" / "clean_data"


# ─── Console helpers ──────────────────────────────────────────────────────────

def log(msg):
    print(f"  \u2714  {msg}")


def warn(msg):
    print(f"  \u26a0  {msg}")


def banner(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# ─── Small helpers ────────────────────────────────────────────────────────────

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def to_decimal(value, default="0"):
    if value is None:
        return decimal.Decimal(default)
    return decimal.Decimal(str(value))


def new_uuid():
    return str(uuid.uuid4())


# ─── Seeding steps ────────────────────────────────────────────────────────────

def seed_categories(cur, categories_raw):
    """
    Upserts every category found by clean_scraped_data.py (both the "key"
    taxonomy - Flower, Edibles, ... - and the promotional/seasonal sections
    for the shop page), keyed by slug. Returns {slug: category_id}.

    is_active always defaults True on first insert. On re-runs it's left
    alone (a category the person turned off in the admin shouldn't be
    silently flipped back on just because it re-appears in a scrape) —
    only name/is_key are refreshed.
    """
    banner("Categories")
    ids = {}
    for cat in categories_raw:
        slug = cat["slug"]
        cur.execute(
            """
            INSERT INTO categories (id, name, slug, description, is_active, is_key, meta_title, meta_description)
            VALUES (%(id)s, %(name)s, %(slug)s, '', TRUE, %(is_key)s, '', '')
            ON CONFLICT (slug) DO UPDATE SET
                name   = EXCLUDED.name,
                is_key = EXCLUDED.is_key
            RETURNING id, (xmax = 0) AS inserted
            """,
            {"id": new_uuid(), "name": cat["name"], "slug": slug, "is_key": cat["is_key"]},
        )
        cat_id, inserted = cur.fetchone()
        ids[slug] = cat_id
        log(f"{'created' if inserted else 'exists '}  {cat['name']} ({'key' if cat['is_key'] else 'section'})")
    return ids


def seed_brands(cur, brands_raw):
    banner("Brands")
    ids = {}
    for raw in brands_raw:
        slug = slugify(raw["name"])
        cur.execute(
            """
            INSERT INTO brands (id, name, slug, description, logo_url, website, is_active, meta_title, meta_description)
            VALUES (%(id)s, %(name)s, %(slug)s, %(description)s, %(logo_url)s, %(website)s, TRUE, '', '')
            ON CONFLICT (slug) DO UPDATE SET
                name        = EXCLUDED.name,
                description = EXCLUDED.description,
                logo_url    = EXCLUDED.logo_url,
                website     = EXCLUDED.website
            RETURNING id
            """,
            {
                "id": new_uuid(),
                "name": raw["name"],
                "slug": slug,
                "description": raw.get("description") or "",
                "logo_url": raw.get("logo_url") or "",
                "website": raw.get("website") or "",
            },
        )
        (brand_id,) = cur.fetchone()
        ids[raw["name"]] = brand_id
    log(f"seeded {len(ids)} brands")
    return ids


def seed_effects(cur, all_effect_names):
    if not all_effect_names:
        return {}
    ids = {}
    for name in sorted(all_effect_names):
        slug = slugify(name)
        cur.execute(
            """
            INSERT INTO effects (id, name, slug)
            VALUES (%(id)s, %(name)s, %(slug)s)
            ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
            """,
            {"id": new_uuid(), "name": name, "slug": slug},
        )
        (effect_id,) = cur.fetchone()
        ids[name] = effect_id
    return ids


def get_or_create_warehouse(cur, name):
    cur.execute("SELECT id FROM warehouses WHERE name = %s LIMIT 1", (name,))
    row = cur.fetchone()
    if row:
        log(f"using warehouse: {name}")
        return row[0]
    warehouse_id = new_uuid()
    cur.execute(
        """
        INSERT INTO warehouses (id, name, address, is_active)
        VALUES (%s, %s, %s, TRUE)
        """,
        (warehouse_id, name, "Imported from scrape — update address"),
    )
    log(f"created warehouse: {name}")
    return warehouse_id


def unique_slug(cur, base_slug, exclude_external_source_id):
    """Same slug-collision handling as before, just via a direct query
    instead of the ORM: only bumps the slug if it's held by a *different*
    product (a re-run against the same source_id should keep its slug)."""
    slug = base_slug
    n = 2
    while True:
        cur.execute(
            "SELECT external_source_id FROM products WHERE slug = %s LIMIT 1",
            (slug,),
        )
        row = cur.fetchone()
        if row is None or row[0] == exclude_external_source_id:
            return slug
        slug = f"{base_slug}-{n}"
        n += 1


def seed_product(cur, raw, category_ids, brand_ids, effect_ids, warehouse_id):
    name = raw["name"] or f"Untitled ({raw['source_id']})"
    base_slug = raw["slug"] or slugify(name)
    slug = unique_slug(cur, base_slug, raw["source_id"])
    brand_id = brand_ids.get(raw["brand_name"])

    cur.execute(
        """
        INSERT INTO products (
            id, name, slug, description, base_price, is_active,
            meta_title, meta_description, is_featured, is_new, compliance_category,
            cannabis_type, sub_type, units_sold_hint, brand_id,
            external_source_id, created_at, updated_at
        )
        VALUES (
            %(id)s, %(name)s, %(slug)s, %(description)s, %(base_price)s, %(is_active)s,
            '', %(meta_description)s, %(is_featured)s, %(is_new)s, %(compliance_category)s,
            %(cannabis_type)s, %(sub_type)s, %(units_sold_hint)s, %(brand_id)s,
            %(external_source_id)s, now(), now()
        )
        ON CONFLICT (external_source_id) DO UPDATE SET
            name                = EXCLUDED.name,
            slug                = EXCLUDED.slug,
            description         = EXCLUDED.description,
            base_price          = EXCLUDED.base_price,
            is_active           = EXCLUDED.is_active,
            meta_description    = EXCLUDED.meta_description,
            is_featured         = EXCLUDED.is_featured,
            is_new              = EXCLUDED.is_new,
            compliance_category = EXCLUDED.compliance_category,
            cannabis_type       = EXCLUDED.cannabis_type,
            sub_type            = EXCLUDED.sub_type,
            units_sold_hint     = EXCLUDED.units_sold_hint,
            brand_id            = EXCLUDED.brand_id,
            updated_at          = now()
        RETURNING id
        """,
        {
            "id": new_uuid(),
            "name": name,
            "slug": slug,
            "description": raw["description"] or "",
            "base_price": to_decimal(raw["pricing"]["price"]),
            "is_active": raw["status"]["is_active"],
            "meta_description": (raw["short_description"] or "")[:160],
            "is_featured": raw["status"]["is_featured"],
            "is_new": raw["status"]["is_new"],
            "compliance_category": raw["compliance_category"] or "",
            "cannabis_type": raw["cannabis_type"] or "",
            "sub_type": raw["sub_type"] or "",
            "units_sold_hint": raw["inventory"]["total_sold"],
            "brand_id": brand_id,
            "external_source_id": raw["source_id"],
        },
    )
    (product_id,) = cur.fetchone()

    # --- categories (M2M) -----------------------------------------------------
    cur.execute("DELETE FROM products_categories WHERE product_id = %s", (product_id,))
    cat_ids = {category_ids[slug] for slug in raw["category_slugs"] if slug in category_ids}
    for cat_id in cat_ids:
        cur.execute(
            "INSERT INTO products_categories (product_id, category_id) VALUES (%s, %s)",
            (product_id, cat_id),
        )

    # --- effects (M2M) ---------------------------------------------------------
    cur.execute("DELETE FROM products_effects WHERE product_id = %s", (product_id,))
    for effect_name in raw["effects"]:
        effect_id = effect_ids.get(effect_name)
        if effect_id:
            cur.execute(
                "INSERT INTO products_effects (product_id, effect_id) VALUES (%s, %s)",
                (product_id, effect_id),
            )

    # --- variant -----------------------------------------------------------------
    sku = raw["sku"] or f"SCR-{raw['source_id'][:16]}"
    cur.execute(
        """
        INSERT INTO product_variants (
            id, product_id, sku, price, is_active, weight_value, weight_unit
        )
        VALUES (%(id)s, %(product_id)s, %(sku)s, %(price)s, %(is_active)s, %(weight_value)s, %(weight_unit)s)
        ON CONFLICT (sku) DO UPDATE SET
            product_id   = EXCLUDED.product_id,
            price        = EXCLUDED.price,
            is_active    = EXCLUDED.is_active,
            weight_value = EXCLUDED.weight_value,
            weight_unit  = EXCLUDED.weight_unit
        RETURNING id
        """,
        {
            "id": new_uuid(),
            "product_id": product_id,
            "sku": sku,
            "price": to_decimal(raw["pricing"]["price_with_discounts"] or raw["pricing"]["price"]),
            "is_active": raw["status"]["is_active"],
            "weight_value": to_decimal(raw["weight"]["value"]) if raw["weight"]["value"] is not None else None,
            "weight_unit": raw["weight"]["unit"] or "unknown",
        },
    )
    (variant_id,) = cur.fetchone()

    # --- lab ---------------------------------------------------------------------
    compounds = raw["lab"]["compounds"]
    percent_fields = {"thc": "thc_percent", "thca": "thca_percent", "cbd": "cbd_percent",
                       "cbda": "cbda_percent", "cbn": "cbn_percent", "cbg": "cbg_percent"}
    lab_values = {field: None for field in percent_fields.values()}
    for compound, field in percent_fields.items():
        info = compounds.get(compound)
        if info and info.get("unit") == "%":
            lab_values[field] = to_decimal(info["value"])

    has_lab_data = raw["lab"]["potency"] or any(v is not None for v in lab_values.values()) or compounds or raw["coa_url"]
    if has_lab_data:
        cur.execute(
            """
            INSERT INTO product_labs (
                id, variant_id, potency, thc_percent, thca_percent, cbd_percent,
                cbda_percent, cbn_percent, cbg_percent, terpenes, coa_url
            )
            VALUES (
                %(id)s, %(variant_id)s, %(potency)s, %(thc_percent)s, %(thca_percent)s, %(cbd_percent)s,
                %(cbda_percent)s, %(cbn_percent)s, %(cbg_percent)s, %(terpenes)s, %(coa_url)s
            )
            ON CONFLICT (variant_id) DO UPDATE SET
                potency      = EXCLUDED.potency,
                thc_percent  = EXCLUDED.thc_percent,
                thca_percent = EXCLUDED.thca_percent,
                cbd_percent  = EXCLUDED.cbd_percent,
                cbda_percent = EXCLUDED.cbda_percent,
                cbn_percent  = EXCLUDED.cbn_percent,
                cbg_percent  = EXCLUDED.cbg_percent,
                terpenes     = EXCLUDED.terpenes,
                coa_url      = COALESCE(NULLIF(EXCLUDED.coa_url, ''), product_labs.coa_url)
            """,
            {
                "id": new_uuid(),
                "variant_id": variant_id,
                "potency": raw["lab"]["potency"] or "",
                "terpenes": psycopg2.extras.Json({
                    "terpenes": raw["lab"]["terpenes"],
                    "compounds_raw": compounds,
                }),
                "coa_url": raw["coa_url"] or "",
                **lab_values,
            },
        )

    # --- images ------------------------------------------------------------------
    for idx, img in enumerate(raw["images"]):
        order = img["order"]
        cur.execute(
            "SELECT id FROM product_images WHERE product_id = %s AND \"order\" = %s LIMIT 1",
            (product_id, order),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE product_images SET source_url = %s, is_primary = %s WHERE id = %s",
                (img["url"], idx == 0, row[0]),
            )
        else:
            cur.execute(
                """
                INSERT INTO product_images (id, product_id, source_url, is_primary, "order", created_at, alt_text)
                VALUES (%s, %s, %s, %s, %s, now(), '')
                """,
                (new_uuid(), product_id, img["url"], idx == 0, order),
            )

    # --- stock ---------------------------------------------------------------------
    cur.execute(
        """
        INSERT INTO stock (id, variant_id, warehouse_id, quantity, reserved, updated_at)
        VALUES (%s, %s, %s, %s, 0, now())
        ON CONFLICT (variant_id, warehouse_id) DO UPDATE SET
            quantity = EXCLUDED.quantity, updated_at = now()
        """,
        (new_uuid(), variant_id, warehouse_id, raw["inventory"]["quantity"]),
    )

    return product_id


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR),
                         help="Folder with products.json / brands.json / categories.json from clean_scraped_data.py")
    parser.add_argument("--warehouse-name", default="Happy Days LI - Farmingdale")
    parser.add_argument("--dsn", default=None, help="Postgres DSN. Defaults to the DATABASE_URL env var.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    products_path = data_dir / "products.json"
    brands_path = data_dir / "brands.json"
    categories_path = data_dir / "categories.json"
    if not products_path.exists():
        sys.exit(f"ERROR: {products_path} not found — run clean_scraped_data.py first.")

    with open(products_path) as f:
        products = json.load(f)
    with open(brands_path) as f:
        brands_raw = json.load(f)
    with open(categories_path) as f:
        categories_raw = json.load(f)

    if args.limit:
        products = products[: args.limit]

    if args.dry_run:
        banner("Dry run — no database writes")
        print(f"Would seed {len(products)} products, {len(brands_raw)} brands, {len(categories_raw)} categories.")
        return

    load_dotenv()
    dsn = args.dsn or os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("No DSN given and DATABASE_URL is not set.")

    start = time.time()
    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                category_ids = seed_categories(cur, categories_raw)
                brand_ids = seed_brands(cur, brands_raw)
                all_effects = {e for p in products for e in p["effects"]}
                effect_ids = seed_effects(cur, all_effects)
                warehouse_id = get_or_create_warehouse(cur, args.warehouse_name)

        banner("Products")
        seeded, errors = 0, 0
        for i, raw in enumerate(products, 1):
            try:
                with conn:
                    with conn.cursor() as cur:
                        seed_product(cur, raw, category_ids, brand_ids, effect_ids, warehouse_id)
                seeded += 1
                if i % 100 == 0 or i == len(products):
                    log(f"{i}/{len(products)} processed")
            except Exception as exc:
                errors += 1
                warn(f"failed on '{raw.get('name')}' ({raw.get('source_id')}): {exc}")
    finally:
        conn.close()

    elapsed = time.time() - start
    banner("Done")
    print(f"Seeded : {seeded}/{len(products)} products in {elapsed:.1f}s")
    print(f"Errors : {errors}")


if __name__ == "__main__":
    main()
