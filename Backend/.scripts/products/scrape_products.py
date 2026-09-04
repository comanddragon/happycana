import csv
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://9realms.eu"
HAPPY_BASE_URL = "https://api.dispenseapp.com"
HAPPY_STOREFRONT = "https://happydaysli.com"
HAPPY_VENUE_ID = "145c714690909516"
HAPPY_API_KEY = "49dac8e0-7743-11e9-8e3f-a5601eb2e936"
OUTPUT_DIR = Path(__file__).resolve().parents[2] / ".output" / "products"
DELAY = 1.0
MAX_RETRIES = 7
BACKOFF_SECONDS = 2.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/151.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/json",
}

session = requests.Session()
session.headers.update(HEADERS)


def clean_url(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")


def get(url, json=False):
    """Fetch a URL, respecting Retry-After and backing off on transient errors."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                headers={**HEADERS, "Accept": "application/json" if json else HEADERS["Accept"]},
                timeout=30,
            )

            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
                return response.json() if json else response.text

            if attempt == MAX_RETRIES:
                response.raise_for_status()

            retry_after = response.headers.get("Retry-After", "")
            try:
                wait = float(retry_after)
            except ValueError:
                wait = BACKOFF_SECONDS * (2 ** attempt)
            wait = min(wait, 120) + random.uniform(0.25, 1.25)
            print(f"  HTTP {response.status_code}; retrying in {wait:.1f}s ({attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = min(BACKOFF_SECONDS * (2 ** attempt), 120) + random.uniform(0.25, 1.25)
            print(f"  Network error: {exc}; retrying in {wait:.1f}s ({attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)

    raise RuntimeError(f"Unable to fetch {url}")


def price(value):
    try:
        return round(float(value) / 100, 2) if value is not None else None
    except (TypeError, ValueError):
        return value


def tags(value):
    return "|".join(map(str, value)) if isinstance(value, list) else (value or "")


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


def source_id(source, value):
    value = str(value or "").strip()
    return value if ":" in value else f"{source}:{value}"


def product_handle(url):
    match = re.search(r"/products/([^/]+)", urlparse(url).path)
    if not match:
        raise ValueError(f"Invalid product URL: {url}")
    return match.group(1)


def canonical_product_url(url):
    """Remove a collection prefix so one Shopify product has exactly one key."""
    return f"{BASE_URL}/products/{product_handle(url)}"


def get_collections():
    soup = BeautifulSoup(get(f"{BASE_URL}/collections"), "html.parser")
    collections = {}

    for a in soup.select('a[href*="/collections/"]'):
        href = a.get("href")
        if not href:
            continue

        url = clean_url(urljoin(BASE_URL, href))
        path = urlparse(url).path

        if not path.startswith("/collections/"):
            continue

        # path.split("/")[-1] would take the LAST segment, which is wrong
        # for a collection-scoped product link like
        # /collections/thc-flower/products/purple-haze-x-10 (Shopify uses
        # this form for "related products" widgets) - that gave a handle
        # of "purple-haze-x-10" (a product) instead of "thc-flower" (the
        # actual collection). Take the segment right after /collections/
        # instead, which is correct for both a plain collection URL and a
        # collection-scoped product URL.
        after = path[len("/collections/"):].strip("/")
        if not after:
            continue
        handle = after.split("/")[0]

        # A collection-scoped product URL also isn't something we want to
        # treat as "a collection page to crawl for its own listing" - only
        # keep it if it's a genuine collection link (no /products/ suffix).
        if "/products/" in after:
            continue

        title = a.get_text(" ", strip=True) or handle.replace("-", " ").title()

        collections[url] = {
            "handle": handle,
            "title": title,
            "url": url,
        }

    return list(collections.values())


def get_collection_products(collection_url):
    collection_handle = urlparse(collection_url).path.rstrip("/").split("/")[-1]
    products = set()
    page = 1

    while True:
        # Shopify's structured collection feed is independent of the theme's
        # rendered markup, so it does not accidentally include recommendations
        # or become empty when the storefront changes its HTML/CSS.
        payload = get(
            f"{BASE_URL}/collections/{collection_handle}/products.json?limit=250&page={page}",
            json=True,
        )
        rows = payload.get("products", [])
        page_products = {
            f"{BASE_URL}/products/{product['handle']}"
            for product in rows
            if product.get("handle")
        }

        if not page_products:
            break

        before = len(products)
        products.update(page_products)

        if len(products) == before:
            break

        if len(rows) < 250:
            break

        page += 1
        time.sleep(DELAY)

    return sorted(products)


def get_product(url):
    handle = product_handle(url)
    return get(f"{BASE_URL}/products/{handle}.js", json=True)


def normalize_product(product, url):
    return {
        "id": source_id("9realms", product.get("id")),
        "source": "9realms",
        "handle": product.get("handle"),
        "title": product.get("title"),
        "url": url,
        "description": product.get("description"),
        "vendor": product.get("vendor"),
        "product_type": product.get("type"),
        "available": product.get("available"),
        "price": price(product.get("price")),
        "compare_at_price": price(product.get("compare_at_price")),
        "featured_image": product.get("featured_image"),
        "tags": tags(product.get("tags")),
        "cannabis_type": "",
        "effects": "",
        "is_featured": False,
        "is_new": False,
        "units_sold": 0,
        "meta_description": "",
    }

def normalize_images(product):
    rows = []

    for position, image in enumerate(product.get("images", []), 1):
        url = image.get("src") if isinstance(image, dict) else image
        if url:
            rows.append({"product_id": source_id("9realms", product.get("id")), "position": position, "url": url})

    return rows

def normalize_variants(product):
    rows = []

    for variant in product.get("variants", []):
        image = variant.get("featured_image")
        image = image.get("src") if isinstance(image, dict) else image

        rows.append({
            "id": source_id("9realms", variant.get("id")),
            "product_id": source_id("9realms", product.get("id")),
            "title": variant.get("title"),
            "sku": variant.get("sku"),
            "available": variant.get("available"),
            "price": price(variant.get("price")),
            "compare_at_price": price(variant.get("compare_at_price")),
            "option1": variant.get("option1"),
            "option2": variant.get("option2"),
            "option3": variant.get("option3"),
            "featured_image": image,
            "weight_value": "",
            "weight_unit": "",
            "inventory_quantity": "",
            "thc_percent": "",
            "coa_url": "",
        })

    return rows


def happy_get_products(skip, limit=100):
    url = f"{HAPPY_BASE_URL}/v1/venues/{HAPPY_VENUE_ID}/products/"
    headers = {
        **HEADERS,
        "api-key": HAPPY_API_KEY,
        "origin": HAPPY_STOREFRONT,
        "referer": f"{HAPPY_STOREFRONT}/shop/farmingdale/",
        "Accept": "application/json",
    }
    for attempt in range(MAX_RETRIES + 1):
        response = session.get(
            url,
            headers=headers,
            # Dispense's unfiltered endpoint includes thousands of historical
            # POS records. This is the same inventory guard used by the live
            # storefront and limits the feed to currently orderable products.
            params={
                "skip": skip,
                "limit": limit,
                "orderPickUpType": "IN_STORE",
                "quantityMin": 1,
            },
            timeout=30,
        )
        if response.status_code not in {429, 500, 502, 503, 504}:
            response.raise_for_status()
            return response.json()
        if attempt == MAX_RETRIES:
            response.raise_for_status()
        retry_after = response.headers.get("Retry-After", "")
        try:
            wait = float(retry_after)
        except ValueError:
            wait = BACKOFF_SECONDS * (2 ** attempt)
        wait = min(wait, 120) + random.uniform(0.25, 1.25)
        print(f"  Happy Days HTTP {response.status_code}; retrying in {wait:.1f}s")
        time.sleep(wait)
    return {"data": [], "count": 0}


def normalize_happy_product(product):
    category = product.get("productCategoryName") or product.get("type") or "Uncategorized"
    image = product.get("image") or next(
        (item.get("fileUrl") for item in product.get("images", []) if item.get("fileUrl")),
        "",
    )
    return {
        "id": source_id("happydays", product.get("id") or product.get("_id")),
        "source": "happydays",
        "handle": product.get("slug"),
        "title": product.get("name"),
        "url": product.get("productUrl") or f"{HAPPY_STOREFRONT}/shop/farmingdale/products/{product.get('slug', '')}",
        "description": product.get("description") or "",
        "vendor": (product.get("brand") or {}).get("name") or "Happy Days",
        "product_type": category,
        "available": bool(product.get("enable", True) and (product.get("quantity") or 0) > 0),
        "price": product.get("priceWithDiscounts") if product.get("priceWithDiscounts") is not None else product.get("price", 0),
        "compare_at_price": product.get("price") if product.get("priceWithDiscounts") is not None else "",
        "featured_image": image,
        "tags": tags(product.get("terpenes")),
        "cannabis_type": product.get("cannabisType") or "",
        "effects": tags(product.get("effects")),
        "is_featured": bool(product.get("featured")),
        "is_new": bool(product.get("new")),
        "units_sold": product.get("totalQuantitySold") or product.get("quantitySold") or 0,
        "meta_description": product.get("seoDescription") or "",
    }


def normalize_happy_image(product, product_key):
    rows = []
    for position, item in enumerate(product.get("images") or [], 1):
        url = item.get("fileUrl") or item.get("originalFileUrl")
        if url:
            rows.append({"product_id": product_key, "position": position, "url": url})
    if not rows and product.get("image"):
        rows.append({"product_id": product_key, "position": 1, "url": product["image"]})
    return rows


def normalize_happy_variant(product, product_key):
    labs = product.get("labs") or {}
    thc = labs.get("thc") if labs.get("thc") is not None else labs.get("potency")
    thc_unit = str(labs.get("thcContentUnit") or "%").strip().lower()
    try:
        # Lab values measured in mg are not percentages and cannot be stored
        # in the catalog's thc_percent field.
        if thc is not None and ("%" not in thc_unit or float(thc) > 100):
            thc = ""
    except (TypeError, ValueError):
        thc = ""
    return {
        "id": source_id("happydays", product.get("id") or product.get("_id")),
        "product_id": product_key,
        "title": product.get("weightFormatted") or product.get("size") or product.get("subType") or "Default",
        "sku": product.get("sku") or f"HD-{product.get('id')}",
        "available": bool(product.get("enable", True) and (product.get("quantity") or 0) > 0),
        "price": product.get("priceWithDiscounts") if product.get("priceWithDiscounts") is not None else product.get("price", 0),
        "compare_at_price": product.get("price") if product.get("priceWithDiscounts") is not None else "",
        "option1": product.get("weightFormatted") or product.get("size") or "",
        "option2": "",
        "option3": "",
        "featured_image": product.get("image") or "",
        "weight_value": product.get("weight") or "",
        "weight_unit": str(product.get("weightUnit") or "").lower(),
        "inventory_quantity": product.get("quantity") or 0,
        "thc_percent": thc or "",
        "coa_url": (product.get("coa") or {}).get("url", "") if isinstance(product.get("coa"), dict) else product.get("coa") or "",
    }

def write_csv(filename, rows, fields):
    with (OUTPUT_DIR / filename).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(filename):
    path = OUTPUT_DIR / filename
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_progress(collection_rows, products, images, variants, collection_products):
    """Atomically checkpoint all output tables so an interrupted run can resume."""
    tables = (
        ("collections.csv", collection_rows, ["handle", "title", "url"]),
        ("products.csv", [p["data"] for p in products.values()], [
            "id", "source", "handle", "title", "url", "description", "vendor", "product_type",
            "available", "price", "compare_at_price", "featured_image", "tags",
            "cannabis_type", "effects", "is_featured", "is_new", "units_sold", "meta_description",
        ]),
        ("product_images.csv", images, ["product_id", "position", "url"]),
        ("variants.csv", variants, [
            "id", "product_id", "title", "sku", "available", "price",
            "compare_at_price", "option1", "option2", "option3", "featured_image",
            "weight_value", "weight_unit", "inventory_quantity", "thc_percent", "coa_url",
        ]),
        ("collection_products.csv", collection_products, ["collection_handle", "product_id"]),
    )
    for filename, rows, fields in tables:
        temp = (OUTPUT_DIR / filename).with_suffix(".csv.tmp")
        with temp.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        temp.replace(OUTPUT_DIR / filename)

def scrape():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    collections = get_collections()
    product_rows = read_csv("products.csv")
    products = {}
    for row in product_rows:
        if not row.get("url"):
            continue
        source = row.get("source") or ("happydays" if "happydaysli.com" in row["url"] else "9realms")
        row["source"] = source
        row["id"] = source_id(source, row.get("id"))
        key = row["url"] if source == "happydays" else canonical_product_url(row["url"])
        row["url"] = key
        products[key] = {"raw": None, "data": row}
    images = read_csv("product_images.csv")
    variants = read_csv("variants.csv")
    collection_products = read_csv("collection_products.csv")
    for row in images:
        row["product_id"] = source_id("9realms", row.get("product_id"))
    for row in variants:
        row["product_id"] = source_id("9realms", row.get("product_id"))
        row["id"] = source_id("9realms", row.get("id"))
    for row in collection_products:
        row["product_id"] = source_id("9realms", row.get("product_id"))
    collection_rows = read_csv("collections.csv")

    seen_images = {(row["product_id"], row["url"]) for row in images}
    seen_variants = {row["id"] for row in variants}
    image_product_ids = {row["product_id"] for row in images}
    variant_product_ids = {row["product_id"] for row in variants}
    seen_relationships = {(row["collection_handle"], str(row["product_id"])) for row in collection_products}
    seen_collections = {row["handle"] for row in collection_rows}

    print(f"Found {len(collections)} collections")
    print(f"Resuming with {len(products)} checkpointed products")

    for collection in collections:
        handle = collection["handle"]
        print(f"\n[{collection['title']}]")

        if handle not in seen_collections:
            collection_rows.append(collection)
            seen_collections.add(handle)

        try:
            product_urls = get_collection_products(collection["url"])
        except Exception as e:
            print(f"  Collection error: {e}")
            continue

        print(f"  Found {len(product_urls)} products")

        for url in product_urls:
            try:
                checkpoint = products.get(url)
                checkpoint_id = checkpoint["data"]["id"] if checkpoint else None
                needs_details = (
                    checkpoint is None
                    or checkpoint_id not in image_product_ids
                    or checkpoint_id not in variant_product_ids
                )
                if needs_details:
                    raw = get_product(url)
                    products[url] = {
                        "raw": raw,
                        "data": normalize_product(raw, url),
                    }
                    verb = "+" if checkpoint is None else "refreshed"
                    print(f"  {verb} {raw.get('title', product_handle(url))}")
                    time.sleep(DELAY)

                    for image in normalize_images(raw):
                        key = (image["product_id"], image["url"])
                        if key not in seen_images:
                            images.append(image)
                            seen_images.add(key)
                            image_product_ids.add(image["product_id"])

                    for variant in normalize_variants(raw):
                        if variant["id"] not in seen_variants:
                            variants.append(variant)
                            seen_variants.add(variant["id"])
                            variant_product_ids.add(variant["product_id"])

                product = products[url]["data"]
                product_id = product["id"]
                relationship = (handle, str(product_id))

                if relationship not in seen_relationships:
                    collection_products.append({
                        "collection_handle": handle,
                        "product_id": product_id,
                    })
                    seen_relationships.add(relationship)

                save_progress(collection_rows, products, images, variants, collection_products)

            except Exception as e:
                print(f"  Product error [{url}]: {e}")

    print("\n[Happy Days LI]")
    skip = 0
    limit = 100
    happy_count = 0
    happy_live_ids = set()
    happy_products = {}
    happy_images = []
    happy_variants = []
    happy_relationships = []
    happy_seen_images = set()
    happy_seen_variants = set()
    happy_seen_relationships = set()
    while True:
        payload = happy_get_products(skip, limit)
        rows = payload.get("data", []) if isinstance(payload, dict) else payload
        if not rows:
            break
        for raw in rows:
            normalized = normalize_happy_product(raw)
            if not normalized["id"] or not normalized["handle"]:
                continue
            key = normalized["url"]
            product_key = normalized["id"]
            # Source ID is the authoritative identity. If the API repeats an
            # item under a changed URL, retain only the latest representation.
            happy_products[product_key] = {"raw": raw, "data": normalized}
            happy_live_ids.add(product_key)

            for image in normalize_happy_image(raw, product_key):
                image_key = (image["product_id"], image["url"])
                if image_key not in happy_seen_images:
                    happy_images.append(image)
                    happy_seen_images.add(image_key)

            variant = normalize_happy_variant(raw, product_key)
            if variant["id"] not in happy_seen_variants:
                happy_variants.append(variant)
                happy_seen_variants.add(variant["id"])

            handle = slugify(normalized["product_type"])
            if handle and handle not in seen_collections:
                collection_rows.append({
                    "handle": handle,
                    "title": normalized["product_type"],
                    "url": f"{HAPPY_STOREFRONT}/shop/farmingdale/categories/{handle}",
                })
                seen_collections.add(handle)
            relationship = (handle, product_key)
            if handle and relationship not in happy_seen_relationships:
                happy_relationships.append({"collection_handle": handle, "product_id": product_key})
                happy_seen_relationships.add(relationship)
            happy_count += 1

        print(f"  Fetched {happy_count}/{payload.get('count', happy_count)} products")
        skip += len(rows)
        if len(rows) < limit or skip >= payload.get("count", skip):
            break
        time.sleep(DELAY)

    old_happy_count = sum(
        item["data"].get("source") == "happydays" for item in products.values()
    )
    products = {
        url: item for url, item in products.items()
        if item["data"].get("source") != "happydays"
    }
    products.update({item["data"]["url"]: item for item in happy_products.values()})
    images = [row for row in images if not row["product_id"].startswith("happydays:")] + happy_images
    variants = [row for row in variants if not row["product_id"].startswith("happydays:")] + happy_variants
    collection_products = [
        row for row in collection_products
        if not row["product_id"].startswith("happydays:")
    ] + happy_relationships
    print(f"  Replaced {old_happy_count} checkpoint rows with {len(happy_live_ids)} live products")

    save_progress(collection_rows, products, images, variants, collection_products)

    print("\nDone.")
    print(f"Collections: {len(collection_rows)}")
    print(f"Products: {len(products)}")
    print(f"Images: {len(images)}")
    print(f"Variants: {len(variants)}")
    print(f"Relationships: {len(collection_products)}")


if __name__ == "__main__":
    scrape()
