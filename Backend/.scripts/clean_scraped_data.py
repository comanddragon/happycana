#!/usr/bin/env python3
"""
clean_scraped_data.py

Cleans and normalizes the raw scrape (Dispense-platform export) into a
backend-agnostic intermediate dataset, ready to be fed into
`seed_scraped_products.py`.

This script has NO Django dependency and does not touch your database —
it only reads the raw JSON files and writes clean JSON/CSV. Safe to run
and re-run as many times as you like.

USAGE
-----
    python clean_scraped_data.py \\
        --input  /path/to/scrapped_data/output \\
        --output /path/to/clean_data

Defaults to ./scrapped_data/output -> ./clean_data if not given.

WHAT IT DOES
------------
1. Loads `shop-all.json` as the master product catalog (it contains
   essentially every product), then scans every other *.json file in the
   input directory for any product ids that are missing from it (there is
   normally at most a handful — campaign/holiday pages are near-total
   subsets of shop-all).
2. Normalizes each raw product into a flat, well-typed schema — cannabis
   classification, potency/lab data, weight/dose, pricing, images, brand,
   external POS ids — regardless of whether your backend has columns for
   all of it yet (see MISSING_FIELDS.md).
3. Deduplicates brands into their own file.
4. Writes a data-quality report so you know what's missing/dirty before
   you seed it.

OUTPUT FILES (in --output)
---------------------------
    products.json    - list of cleaned product records (each carries a
                        `category_slugs` list - which scraped category
                        pages, key + promotional/seasonal, it appears in)
    brands.json       - list of deduped brand records
    categories.json    - one row per distinct category slug seen across all
                          products, with a humanized name and `is_key`
                          (main taxonomy) vs promotional/seasonal section
    products.csv        - flat CSV for a quick spreadsheet skim
    report.json           - machine-readable data-quality summary
"""

import argparse
import csv
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR = BACKEND_DIR / ".output" / "categories"
DEFAULT_OUTPUT_DIR = BACKEND_DIR / ".output" / "clean_data"

# ─── Reference data ──────────────────────────────────────────────────────────

# Raw values are already SCREAMING_SNAKE / matching our target lower_snake
# choices almost exactly - this exists mainly as a safety net + single
# place to fix if the source data ever changes casing/spelling.
COMPLIANCE_CATEGORY_MAP = {
    "FLOWER": "flower",
    "VAPORIZERS": "vaporizers",
    "EDIBLES": "edibles",
    "CONCENTRATES": "concentrates",
    "PRE_ROLLS": "pre_rolls",
    "TINCTURES": "tinctures",
    "TOPICALS": "topicals",
    "BEVERAGES": "beverages",
    "ACCESSORIES": "accessories",
    "MERCHANDISE": "merchandise",
    "CBD_PRODUCTS": "cbd_products",
    "GIFT_CARDS": "gift_cards",
}

CANNABIS_TYPE_MAP = {
    "SATIVA": "sativa",
    "INDICA": "indica",
    "HYBRID": "hybrid",
    "HYBRID_SATIVA": "hybrid_sativa",
    "HYBRID_INDICA": "hybrid_indica",
    "NA": "na",
}

WEIGHT_UNIT_MAP = {
    "GRAMS": "grams",
    "MILLIGRAMS": "milligrams",
    "UNKNOWN": "unknown",
}

# Cannabinoid compounds present as {compound}/{compound}ContentUnit pairs
# inside the raw `labs` object.
LAB_COMPOUNDS = ["thc", "thcA", "cbd", "cbdA", "cbn", "cbg"]

# Terpenes present the same way inside `labs`. Not every product has all of
# these - most have 0-9 of them populated.
LAB_TERPENES = [
    "alphaPinene", "betaCaryophyllene", "betaEudesmol", "betaMyrcene",
    "betaPinene", "bisabolol", "caryophylleneOxide", "guaiol", "humulene",
    "limonene", "linalool", "ocimene", "terpinene", "terpinolene",
    "threeCarene", "transNerolidol",
]

# Files that aren't real product listings - skip when scanning for
# "products missing from shop-all".
NON_PRODUCT_FILES = {"shop-all.json", "category_analysis.json"}

# scrapper.v2.py writes one file per category page, slugified from its
# name/slug on the source site (e.g. "flower.json", "710.json"). The
# handful matching our own compliance categories are the main taxonomy
# ("key" categories) - everything else scraped (holidays, campaigns,
# "microgrowers", ...) is a promotional/seasonal section for the shop page.
KEY_CATEGORY_SLUGS = {v.replace("_", "-") for v in COMPLIANCE_CATEGORY_MAP.values()}

# A few slugs read oddly when title-cased word-by-word - spelled out here
# instead of guessing at humanization rules.
CATEGORY_NAME_OVERRIDES = {
    "cbd-products": "CBD Products",
    "710": "710",
    "100-spend-secret-menu": "$100 Spend Secret Menu",
}


def humanize_category_slug(slug: str) -> str:
    if slug in CATEGORY_NAME_OVERRIDES:
        return CATEGORY_NAME_OVERRIDES[slug]
    return " ".join(word.capitalize() for word in slug.split("-"))


# ─── Small helpers ───────────────────────────────────────────────────────────

def camel_to_snake(name: str) -> str:
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return s.lower()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def clean_html(raw):
    """Strip <br/> tags to newlines, drop any other tags, unescape entities."""
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    # Collapse runs of blank lines/spaces produced by the tag stripping.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def make_short_description(description: str, seo_description: str, limit=160):
    source = (seo_description or description or "").replace("\n", " ").strip()
    source = re.sub(r"\s+", " ", source)
    if len(source) <= limit:
        return source
    return source[: limit - 1].rsplit(" ", 1)[0] + "…"


def clean_lab(labs: dict):
    if not labs:
        return {"potency": None, "compounds": {}, "terpenes": {}}

    potency = labs.get("potency")
    compounds = {}
    for compound in LAB_COMPOUNDS:
        value = labs.get(compound)
        if value is not None:
            compounds[compound.lower()] = {
                "value": value,
                "unit": labs.get(f"{compound}ContentUnit"),
            }

    terpenes = {}
    for terp in LAB_TERPENES:
        value = labs.get(terp)
        if value is not None:
            terpenes[camel_to_snake(terp)] = {
                "value": value,
                "unit": labs.get(f"{terp}ContentUnit"),
            }

    return {
        "potency": potency.lower() if potency else None,
        "compounds": compounds,
        "terpenes": terpenes,
    }


# ─── Loading raw data ────────────────────────────────────────────────────────

def load_master_products(input_dir: str):
    """
    shop-all.json is the master catalog (near-100% superset). Scan every
    other list file for any product ids it's missing, and also build a
    map of which curated collections/campaigns each product appears in
    (useful metadata, not required for seeding).
    """
    shop_all_path = os.path.join(input_dir, "shop-all.json")
    if not os.path.exists(shop_all_path):
        sys.exit(f"ERROR: expected {shop_all_path} - is --input pointing at the "
                  f"'output' folder from scrapped_data.zip?")

    with open(shop_all_path) as f:
        master = json.load(f)

    by_id = {p["id"]: p for p in master if "id" in p}
    collections = defaultdict(list)

    for fn in sorted(os.listdir(input_dir)):
        if not fn.endswith(".json") or fn in NON_PRODUCT_FILES:
            continue
        path = os.path.join(input_dir, fn)
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"  [skip] {fn}: not valid JSON")
            continue
        if not isinstance(data, list):
            continue

        collection_slug = fn[:-5]
        for item in data:
            pid = item.get("id")
            if not pid:
                continue
            if fn != "shop-all.json":
                collections[pid].append(collection_slug)
            if pid not in by_id:
                by_id[pid] = item  # recover the rare product missing from shop-all

    return list(by_id.values()), collections


# ─── Cleaning a single product ───────────────────────────────────────────────

def clean_product(raw: dict, collections: dict, brands: dict, quality: dict):
    pid = raw.get("id")

    # --- brand -------------------------------------------------------------
    brand_name = None
    raw_brand = raw.get("brand")
    if raw_brand and raw_brand.get("name"):
        brand_name = raw_brand["name"].strip()
        key = brand_name.lower()
        existing = brands.get(key)
        if existing is None:
            brands[key] = {
                "name": brand_name,
                "slug": slugify(brand_name),
                "description": clean_html(raw_brand.get("description")),
                "logo_url": raw_brand.get("logo") or None,
                "website": raw_brand.get("website") or None,
                "source_id": raw_brand.get("id"),
            }
        else:
            # Fill in gaps if a later record has richer brand data than the
            # first one we saw (brand sub-objects are inconsistently rich).
            for field, src in (
                ("description", clean_html(raw_brand.get("description"))),
                ("logo_url", raw_brand.get("logo")),
                ("website", raw_brand.get("website")),
            ):
                if not existing.get(field) and src:
                    existing[field] = src
    else:
        quality["missing_brand"] += 1

    # --- classification ------------------------------------------------------
    raw_compliance = raw.get("cannabisComplianceType")
    compliance_category = COMPLIANCE_CATEGORY_MAP.get(raw_compliance)
    if raw_compliance and not compliance_category:
        quality["unknown_compliance_category"][raw_compliance] += 1

    raw_cannabis_type = raw.get("cannabisType")
    cannabis_type = CANNABIS_TYPE_MAP.get(raw_cannabis_type) if raw_cannabis_type else None
    if raw_cannabis_type and not cannabis_type:
        quality["unknown_cannabis_type"][raw_cannabis_type] += 1

    # --- weight / dose -------------------------------------------------------
    weight_unit = WEIGHT_UNIT_MAP.get(raw.get("weightUnit"))
    weight = {
        "value": raw.get("weight"),
        "unit": weight_unit,
        "grams": raw.get("weightInGrams"),
        "formatted": raw.get("weightFormatted") or None,
    }

    # --- images ---------------------------------------------------------------
    images = []
    for idx, img in enumerate(raw.get("images") or []):
        url = img.get("fileUrl")
        if url:
            images.append({"url": url, "order": img.get("order", idx)})
    if not images:
        quality["missing_images"] += 1

    # --- pricing ---------------------------------------------------------------
    price = raw.get("price")
    if price is None:
        quality["missing_price"] += 1

    description = clean_html(raw.get("description"))
    if not description:
        quality["missing_description"] += 1

    sku = (raw.get("sku") or "").strip() or None
    if sku and (sku.lower().startswith(("http://", "https://")) or len(sku) > 64):
        # Seen in the wild: lab-report / COA URLs pasted into the SKU field
        # upstream. A real SKU is never a URL and your ProductVariant.sku
        # column is varchar(100) - a >100 char value would fail at the DB
        # level (and even under 100, it's clearly not a real SKU). Drop it
        # and let the seed script generate a safe fallback instead.
        quality["invalid_sku_dropped"] += 1
        sku = None
    if not sku:
        quality["missing_sku"] += 1

    record = {
        "source_id": pid,
        "pos_product_id": raw.get("posProductId"),
        "external_ids": {
            "alleaves": (raw.get("alleaves") or {}).get("productId"),
            "weedmaps": (raw.get("weedmaps") or {}).get("productId"),
            "leafly": (raw.get("leafly") or {}).get("productId"),
        },
        "sku": sku,
        "name": (raw.get("name") or "").strip(),
        "slug": raw.get("slug"),
        "description": description,
        "short_description": make_short_description(description, raw.get("seoDescription")),
        "brand_name": brand_name,
        "category_name": raw.get("productCategoryName"),
        "compliance_category": compliance_category,
        "sub_type": (raw.get("subType") or "").strip() or None,
        "cannabis_type": cannabis_type,
        "weight": weight,
        "pricing": {
            "price": price,
            "price_with_discounts": raw.get("priceWithDiscounts"),
            "price_gross": raw.get("priceGross"),
            "discount_type": raw.get("discountTypeFinal"),
            "discount_value": raw.get("discountValueFinal") or 0,
        },
        "inventory": {
            "quantity": raw.get("quantity") or 0,
            "total_sold": raw.get("totalSold") or 0,
        },
        "status": {
            "is_active": bool(raw.get("enable")) and not bool(raw.get("deleted")),
            "is_featured": bool(raw.get("featured")),
            "is_new": bool(raw.get("new")),
        },
        "effects": raw.get("effects") or [],
        "lab": clean_lab(raw.get("labs") or {}),
        "coa_url": raw.get("coa") or None,
        "images": images,
        "product_url": raw.get("productUrl"),
        "review_stats": raw.get("reviewStats"),
        "category_slugs": sorted(set(collections.get(pid, []))),
        "created": raw.get("created"),
        "modified": raw.get("modified"),
    }
    return record


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", default=str(DEFAULT_INPUT_DIR), help="Folder containing shop-all.json etc.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Where to write cleaned files")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(f"Loading raw data from {args.input} ...")
    raw_products, collections = load_master_products(args.input)
    print(f"  {len(raw_products)} unique products found")

    brands = {}
    quality = {
        "missing_brand": 0,
        "missing_images": 0,
        "missing_price": 0,
        "missing_description": 0,
        "missing_sku": 0,
        "invalid_sku_dropped": 0,
        "unknown_compliance_category": Counter(),
        "unknown_cannabis_type": Counter(),
    }

    products = []
    seen_slugs = Counter()
    for raw in raw_products:
        cleaned = clean_product(raw, collections, brands, quality)
        seen_slugs[cleaned["slug"]] += 1
        products.append(cleaned)

    duplicate_slugs = {slug: n for slug, n in seen_slugs.items() if n > 1}

    # Some source SKUs are reused across genuinely different products (seen
    # in the wild: two unrelated products sharing a barcode-looking SKU, and
    # one case where a URL was pasted into the SKU field on two listings).
    # A duplicate SKU would make the seed script's variant lookup silently
    # merge two different products onto one inventory record, so: keep the
    # first occurrence, blank the rest and let the seed script generate a
    # deterministic fallback SKU for them instead.
    sku_counts = Counter(p["sku"] for p in products if p["sku"])
    duplicate_skus = {sku: n for sku, n in sku_counts.items() if n > 1}
    if duplicate_skus:
        seen_once = set()
        for p in products:
            if p["sku"] in duplicate_skus:
                if p["sku"] in seen_once:
                    p["sku"] = None
                else:
                    seen_once.add(p["sku"])

    by_compliance = Counter(p["compliance_category"] for p in products)

    # --- write outputs -----------------------------------------------------
    products_path = os.path.join(args.output, "products.json")
    with open(products_path, "w") as f:
        json.dump(products, f, indent=2)

    brands_list = sorted(brands.values(), key=lambda b: b["name"].lower())
    brands_path = os.path.join(args.output, "brands.json")
    with open(brands_path, "w") as f:
        json.dump(brands_list, f, indent=2)

    all_category_slugs = sorted({slug for p in products for slug in p["category_slugs"]})
    categories_path = os.path.join(args.output, "categories.json")
    with open(categories_path, "w") as f:
        json.dump(
            [
                {
                    "slug": slug,
                    "name": humanize_category_slug(slug),
                    "is_key": slug in KEY_CATEGORY_SLUGS,
                }
                for slug in all_category_slugs
            ],
            f, indent=2,
        )

    csv_path = os.path.join(args.output, "products.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_id", "sku", "name", "brand_name", "compliance_category",
            "sub_type", "cannabis_type", "weight_formatted", "price", "quantity",
            "is_active", "image_count",
        ])
        for p in products:
            writer.writerow([
                p["source_id"], p["sku"], p["name"], p["brand_name"],
                p["compliance_category"], p["sub_type"], p["cannabis_type"],
                p["weight"]["formatted"], p["pricing"]["price"],
                p["inventory"]["quantity"], p["status"]["is_active"],
                len(p["images"]),
            ])

    report = {
        "total_products": len(products),
        "total_brands": len(brands_list),
        "products_by_compliance_category": by_compliance,
        "duplicate_slugs": duplicate_slugs,
        "duplicate_skus_found_and_reset": duplicate_skus,
        **{k: v for k, v in quality.items()},
    }
    report_path = os.path.join(args.output, "report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=dict)

    # --- human-readable summary ----------------------------------------------
    print()
    print("=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)
    print(f"Products cleaned : {len(products)}")
    print(f"Brands found     : {len(brands_list)}")
    key_count = sum(1 for s in all_category_slugs if s in KEY_CATEGORY_SLUGS)
    print(f"Categories found : {len(all_category_slugs)} ({key_count} key, {len(all_category_slugs) - key_count} sections)")
    print()
    print("By compliance category:")
    for cat, count in by_compliance.most_common():
        print(f"  {cat or '(unclassified)':15} {count}")
    print()
    print("Data quality flags:")
    print(f"  Missing brand        : {quality['missing_brand']}")
    print(f"  Missing image        : {quality['missing_images']}")
    print(f"  Missing price        : {quality['missing_price']}")
    print(f"  Missing description  : {quality['missing_description']}")
    print(f"  Missing SKU          : {quality['missing_sku']} (falls back to slug-based SKU at seed time)")
    print(f"  Invalid SKU dropped  : {quality['invalid_sku_dropped']} (was a URL or too long — see MISSING_FIELDS.md)")
    if quality["unknown_compliance_category"]:
        print(f"  Unrecognized compliance categories: {dict(quality['unknown_compliance_category'])}")
    if quality["unknown_cannabis_type"]:
        print(f"  Unrecognized cannabis types: {dict(quality['unknown_cannabis_type'])}")
    if duplicate_slugs:
        print(f"  Duplicate slugs: {duplicate_slugs}")
    if duplicate_skus:
        print(f"  Duplicate SKUs reused across different products (blanked, will get a")
        print(f"  generated fallback SKU at seed time — check the source data): {list(duplicate_skus)}")
    print()
    print(f"Wrote: {products_path}")
    print(f"Wrote: {brands_path}")
    print(f"Wrote: {categories_path}")
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {report_path}")
    print()
    print("Next: run seed_scraped_products.py against this output/ folder.")


if __name__ == "__main__":
    main()