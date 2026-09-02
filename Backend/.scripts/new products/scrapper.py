import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://9realms.eu"
OUTPUT_DIR = Path("scraped_data")
DELAY = 0.25

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
    response = session.get(
        url,
        headers={**HEADERS, "Accept": "application/json" if json else HEADERS["Accept"]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json() if json else response.text


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

        handle = path.rstrip("/").split("/")[-1]
        title = a.get_text(" ", strip=True) or handle.replace("-", " ").title()

        collections[url] = {
            "handle": handle,
            "title": title,
            "url": url,
        }

    return list(collections.values())


def get_collection_products(collection_url):
    products = set()
    page = 1

    while True:
        url = f"{collection_url}?page={page}"
        soup = BeautifulSoup(get(url), "html.parser")

        page_products = {
            clean_url(urljoin(BASE_URL, a["href"]))
            for a in soup.select('a[href*="/products/"]')
            if a.get("href")
        }

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

def scrape():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    collections = get_collections()
    products = {}
    images = []
    variants = []
    collection_products = []
    collection_rows = []

    seen_images = set()
    seen_variants = set()
    seen_relationships = set()

    print(f"Found {len(collections)} collections")

    for collection in collections:
        handle = collection["handle"]
        print(f"\n[{collection['title']}]")

        collection_rows.append(collection)

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
                relationship = (handle, product_id)

                if relationship not in seen_relationships:
                    collection_products.append({
                        "collection_handle": handle,
                        "product_id": product_id,
                    })
                    seen_relationships.add(relationship)

            except Exception as e:
                print(f"  Product error [{url}]: {e}")

    write_csv(
        "collections.csv",
        collection_rows,
        ["handle", "title", "url"],
    )

    write_csv(
        "products.csv",
        [p["data"] for p in products.values()],
        [
            "id",
            "handle",
            "title",
            "url",
            "description",
            "vendor",
            "product_type",
            "available",
            "price",
            "compare_at_price",
            "featured_image",
            "tags",
        ],
    )

    write_csv(
        "product_images.csv",
        images,
        ["product_id", "position", "url"],
    )

    write_csv(
        "variants.csv",
        variants,
        [
            "id",
            "product_id",
            "title",
            "sku",
            "available",
            "price",
            "compare_at_price",
            "option1",
            "option2",
            "option3",
            "featured_image",
        ],
    )

    write_csv(
        "collection_products.csv",
        collection_products,
        ["collection_handle", "product_id"],
    )

    print("\nDone.")
    print(f"Collections: {len(collection_rows)}")
    print(f"Products: {len(products)}")
    print(f"Images: {len(images)}")
    print(f"Variants: {len(variants)}")
    print(f"Relationships: {len(collection_products)}")


if __name__ == "__main__":
    scrape()