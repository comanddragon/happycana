import csv
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://9realms.eu"
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
        url = f"{collection_url}?page={page}"
        soup = BeautifulSoup(get(url), "html.parser")

        page_products = set()
        for a in soup.select('a[href*="/products/"]'):
            href = a.get("href")
            if not href:
                continue
            product_url = clean_url(urljoin(BASE_URL, href))
            path = urlparse(product_url).path

            # A collection-scoped product link (/collections/{X}/products/{p})
            # pointing at a DIFFERENT collection than the one we're crawling
            # is a cross-sell/"related products" widget, not a real member of
            # this collection - drop it. This was the main source of every
            # product ending up tagged into nearly every collection.
            #
            # NOTE: a bare /products/{handle} link (no /collections/ prefix)
            # can't be disambiguated this way - if the theme also renders a
            # same-page widget using bare links, those would still slip
            # through here. Re-scrape and spot-check collection membership
            # after this fix; if it's still over-broad, the real fix is
            # scoping the CSS selector to the actual product-grid container
            # element, which needs eyes on the live page markup to get right.
            if path.startswith("/collections/") and "/products/" in path:
                scoped_handle = path[len("/collections/"):].split("/")[0]
                if scoped_handle != collection_handle:
                    continue

            page_products.add(canonical_product_url(product_url))

        if not page_products:
            break

        before = len(products)
        products.update(page_products)

        if len(products) == before:
            break

        page += 1
        time.sleep(DELAY)

    return sorted(products)


def get_product(url):
    handle = product_handle(url)
    return get(f"{BASE_URL}/products/{handle}.js", json=True)


def normalize_product(product, url):
    return {
        "id": product.get("id"),
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
    }

def normalize_images(product):
    rows = []

    for position, image in enumerate(product.get("images", []), 1):
        url = image.get("src") if isinstance(image, dict) else image
        if url:
            rows.append({"product_id": product.get("id"), "position": position, "url": url})

    return rows

def normalize_variants(product):
    rows = []

    for variant in product.get("variants", []):
        image = variant.get("featured_image")
        image = image.get("src") if isinstance(image, dict) else image

        rows.append({
            "id": variant.get("id"),
            "product_id": product.get("id"),
            "title": variant.get("title"),
            "sku": variant.get("sku"),
            "available": variant.get("available"),
            "price": price(variant.get("price")),
            "compare_at_price": price(variant.get("compare_at_price")),
            "option1": variant.get("option1"),
            "option2": variant.get("option2"),
            "option3": variant.get("option3"),
            "featured_image": image,
        })

    return rows

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
            "id", "handle", "title", "url", "description", "vendor", "product_type",
            "available", "price", "compare_at_price", "featured_image", "tags",
        ]),
        ("product_images.csv", images, ["product_id", "position", "url"]),
        ("variants.csv", variants, [
            "id", "product_id", "title", "sku", "available", "price",
            "compare_at_price", "option1", "option2", "option3", "featured_image",
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
        url = canonical_product_url(row["url"])
        row["url"] = url
        products[url] = {"raw": None, "data": row}
    images = read_csv("product_images.csv")
    variants = read_csv("variants.csv")
    collection_products = read_csv("collection_products.csv")
    collection_rows = read_csv("collections.csv")

    seen_images = {(row["product_id"], row["url"]) for row in images}
    seen_variants = {row["id"] for row in variants}
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
                if url not in products:
                    raw = get_product(url)
                    products[url] = {
                        "raw": raw,
                        "data": normalize_product(raw, url),
                    }
                    print(f"  + {raw.get('title', product_handle(url))}")
                    time.sleep(DELAY)

                    for image in normalize_images(raw):
                        key = (image["product_id"], image["url"])
                        if key not in seen_images:
                            images.append(image)
                            seen_images.add(key)

                    for variant in normalize_variants(raw):
                        if variant["id"] not in seen_variants:
                            variants.append(variant)
                            seen_variants.add(variant["id"])

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

    save_progress(collection_rows, products, images, variants, collection_products)

    print("\nDone.")
    print(f"Collections: {len(collection_rows)}")
    print(f"Products: {len(products)}")
    print(f"Images: {len(images)}")
    print(f"Variants: {len(variants)}")
    print(f"Relationships: {len(collection_products)}")


if __name__ == "__main__":
    scrape()
