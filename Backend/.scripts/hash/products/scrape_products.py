"""Scrape Frozen Hashish's public WooCommerce catalog into CSV checkpoints.

The Store API supplies products, categories, availability, and images. Variable
prices are read from WooCommerce's public product-variation form data.

Examples:
    python scrape_products.py
    python scrape_products.py --category dry-sift-hash --limit 20
"""

import argparse
import csv
import html
import json
import random
import re
import time
from decimal import Decimal
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://frozenhashish.com"
API_URL = f"{BASE_URL}/wp-json/wc/store/v1"
SOURCE = "frozenhashish"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / ".output" / "hash" / "products"
HASH_CATEGORY_SLUGS = {
    "cali-plates-hash",
    "commercial-hash",
    "dry-filtered-hash-3x",
    "dry-sift-hash",
    "frozen-hash-frozen-shift",
    "hashish-eggs-hash",
    "la-mousse-hash",
    "static-sift-hash",
}
RETRY_STATUS = {429, 500, 502, 503, 504}
HEADERS = {
    "User-Agent": "CatalogResearchBot/1.0 (+local catalog import; respects robots.txt)",
    "Accept": "application/json,text/html;q=0.9",
}


def get(session, url, *, as_json=False, max_retries=5):
    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, timeout=30)
            if response.status_code not in RETRY_STATUS:
                response.raise_for_status()
                return response.json() if as_json else response.text
            if attempt == max_retries:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After", "")
            try:
                wait = float(retry_after)
            except ValueError:
                wait = min(2 ** attempt, 60) + random.uniform(0.2, 0.8)
            print(f"HTTP {response.status_code}; retrying in {wait:.1f}s")
            time.sleep(wait)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == max_retries:
                raise
            time.sleep(min(2 ** attempt, 60) + random.uniform(0.2, 0.8))
    raise RuntimeError(f"Unable to fetch {url}")


def source_id(value):
    return f"{SOURCE}:{value}"


def plain_text(value):
    soup = BeautifulSoup(value or "", "html.parser")
    for node in soup.select("script, style"):
        node.decompose()
    return soup.get_text("\n", strip=True)


def money(prices, key="price"):
    raw = prices.get(key)
    if raw in (None, ""):
        return ""
    minor_unit = int(prices.get("currency_minor_unit", 2))
    return str(Decimal(str(raw)) / (Decimal(10) ** minor_unit))


def potency(text):
    values = {"thc_percent": "", "thca_percent": "", "cbd_percent": ""}
    for amount, cannabinoid in re.findall(r"(\d+(?:\.\d+)?)\s*%\s*(THCA|THC|CBD)\b", text or "", re.IGNORECASE):
        key = f"{cannabinoid.lower()}_percent"
        values[key] = amount
    return values


def weight(value):
    match = re.search(r"(\d+(?:\.\d+)?)\s*(mg|g|grams?)\b", value or "", re.IGNORECASE)
    if not match:
        return "", ""
    amount, unit = match.groups()
    return amount, "milligrams" if unit.lower() == "mg" else "grams"


def parse_variations(page_html, product):
    soup = BeautifulSoup(page_html, "html.parser")
    form = soup.select_one("form.variations_form[data-product_variations]")
    if not form:
        return []
    raw = html.unescape(form.get("data-product_variations", ""))
    if not raw:
        return []
    rows = []
    for variation in json.loads(raw):
        attributes = variation.get("attributes") or {}
        label = " / ".join(str(value) for value in attributes.values() if value) or "Default"
        weight_value, weight_unit = weight(label or variation.get("weight", ""))
        image = variation.get("image") or {}
        rows.append({
            "id": source_id(variation["variation_id"]),
            "product_id": source_id(product["id"]),
            "name": label,
            "sku": variation.get("sku") or f"FH-{variation['variation_id']}",
            "price": str(variation.get("display_price", "")),
            "compare_at_price": str(variation.get("display_regular_price", "")),
            "available": bool(variation.get("variation_is_active") and variation.get("is_in_stock")),
            "weight_value": weight_value,
            "weight_unit": weight_unit,
            "image_url": image.get("full_src") or image.get("url") or image.get("src") or "",
        })
    return rows


def default_variant(product):
    weight_value, weight_unit = weight(product.get("weight") or product.get("formatted_weight"))
    prices = product.get("prices") or {}
    return {
        "id": source_id(product["id"]),
        "product_id": source_id(product["id"]),
        "name": product.get("formatted_weight") if product.get("formatted_weight") != "N/A" else "Default",
        "sku": product.get("sku") or f"FH-{product['id']}",
        "price": money(prices),
        "compare_at_price": money(prices, "regular_price"),
        "available": bool(product.get("is_in_stock") and product.get("is_purchasable")),
        "weight_value": weight_value,
        "weight_unit": weight_unit,
        "image_url": "",
    }


def write_csv(output_dir, filename, rows, fields):
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / filename
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(target)


def save(output_dir, categories, products, images, variants, memberships):
    write_csv(output_dir, "categories.csv", categories, ["id", "slug", "name", "description", "source_url"])
    write_csv(output_dir, "products.csv", products, [
        "id", "source_url", "slug", "name", "description", "short_description",
        "base_price", "compare_at_price", "currency", "available", "product_type",
        "thc_percent", "thca_percent", "cbd_percent",
    ])
    write_csv(output_dir, "images.csv", images, ["product_id", "position", "url", "alt_text"])
    write_csv(output_dir, "variants.csv", variants, [
        "id", "product_id", "name", "sku", "price", "compare_at_price", "available",
        "weight_value", "weight_unit", "image_url",
    ])
    write_csv(output_dir, "category_products.csv", memberships, ["category_id", "product_id"])


def scrape(args):
    session = requests.Session()
    session.headers.update(HEADERS)
    category_payload = get(session, f"{API_URL}/products/categories?per_page=100", as_json=True)
    wanted = [row for row in category_payload if row.get("slug") in HASH_CATEGORY_SLUGS]
    if args.category:
        wanted = [row for row in wanted if row["slug"] in args.category]
    if not wanted:
        raise SystemExit("No matching hash categories were found.")

    categories = [{
        "id": source_id(row["id"]),
        "slug": row["slug"],
        "name": row["name"],
        "description": plain_text(row.get("description")),
        "source_url": row.get("permalink", ""),
    } for row in wanted]
    products_by_id = {}
    memberships = set()
    for category in wanted:
        page = 1
        while True:
            payload = get(
                session,
                f"{API_URL}/products?category={category['id']}&per_page=100&page={page}",
                as_json=True,
            )
            for product in payload:
                key = source_id(product["id"])
                products_by_id[key] = product
                memberships.add((source_id(category["id"]), key))
            print(f"{category['name']} page {page}: {len(payload)} products")
            if len(payload) < 100:
                break
            page += 1
            if args.delay:
                time.sleep(args.delay)

    selected = list(products_by_id.values())
    if args.limit is not None:
        selected = selected[:args.limit]
    selected_ids = {source_id(row["id"]) for row in selected}
    memberships = [
        {"category_id": category_id, "product_id": product_id}
        for category_id, product_id in sorted(memberships)
        if product_id in selected_ids
    ]

    products = []
    images = []
    variants = []
    for index, product in enumerate(selected, 1):
        key = source_id(product["id"])
        category_names = [row["name"] for row in product.get("categories", []) if row.get("slug") in HASH_CATEGORY_SLUGS]
        product_type = " / ".join(category_names) or "Hash"
        product_prices = product.get("prices") or {}
        inferred = potency(f"{product.get('name', '')} {plain_text(product.get('short_description'))}")
        products.append({
            "id": key,
            "source_url": product.get("permalink", ""),
            "slug": product.get("slug", ""),
            "name": product.get("name", ""),
            "description": plain_text(product.get("description")),
            "short_description": plain_text(product.get("short_description")),
            "base_price": money(product_prices),
            "compare_at_price": money(product_prices, "regular_price"),
            "currency": product_prices.get("currency_code", "EUR"),
            "available": bool(product.get("is_in_stock") and product.get("is_purchasable")),
            "product_type": product_type,
            **inferred,
        })
        for position, image in enumerate(product.get("images") or [], 1):
            if image.get("src"):
                images.append({
                    "product_id": key,
                    "position": position,
                    "url": image["src"],
                    "alt_text": image.get("alt") or product.get("name", ""),
                })
        product_variants = []
        if product.get("type") == "variable":
            product_variants = parse_variations(get(session, product["permalink"]), product)
        variants.extend(product_variants or [default_variant(product)])
        print(f"[{index}/{len(selected)}] {product.get('name')} ({len(product_variants) or 1} variants)")
        if args.delay and index < len(selected):
            time.sleep(args.delay)
        if index % 20 == 0:
            save(args.output_dir, categories, products, images, variants, memberships)

    save(args.output_dir, categories, products, images, variants, memberships)
    print(f"Wrote {len(products)} products, {len(variants)} variants, and {len(images)} images to {args.output_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--category", action="append", choices=sorted(HASH_CATEGORY_SLUGS))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay", type=float, default=0.25)
    return parser.parse_args()


if __name__ == "__main__":
    scrape(parse_args())
