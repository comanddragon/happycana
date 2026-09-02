import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://9realms.eu"
COLLECTIONS_URL = f"{BASE_URL}/collections"
OUTPUT_FILE = Path("products_by_collection.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/json",
}


session = requests.Session()
session.headers.update(HEADERS)


def clean_url(url: str) -> str:
    """
    Remove query strings/fragments and normalize trailing slash.
    """
    parsed = urlparse(url)

    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def get_html(url: str) -> str:
    """
    Fetch an HTML page.
    """
    response = session.get(url, timeout=30)
    response.raise_for_status()

    return response.text


def get_collection_links() -> list[dict]:
    """
    Extract collection links from /collections.
    """

    print(f"Fetching collections page: {COLLECTIONS_URL}")

    html = get_html(COLLECTIONS_URL)
    soup = BeautifulSoup(html, "html.parser")

    collections = {}

    for link in soup.select('a[href*="/collections/"]'):
        href = link.get("href")

        if not href:
            continue

        url = clean_url(urljoin(BASE_URL, href))

        parsed = urlparse(url)

        if not parsed.path.startswith("/collections/"):
            continue

        handle = parsed.path.rstrip("/").split("/")[-1]

        if not handle:
            continue

        title = link.get_text(" ", strip=True)

        if not title:
            title = handle.replace("-", " ").title()

        collections[url] = {
            "handle": handle,
            "title": title,
            "url": url,
        }

    return list(collections.values())


def get_product_links(collection_url: str) -> list[str]:
    """
    Extract product URLs from a collection page.
    """

    print(f"  Fetching collection: {collection_url}")

    html = get_html(collection_url)
    soup = BeautifulSoup(html, "html.parser")

    products = set()

    for link in soup.select('a[href*="/products/"]'):
        href = link.get("href")

        if not href:
            continue

        url = clean_url(urljoin(BASE_URL, href))

        parsed = urlparse(url)

        if not parsed.path.startswith("/products/"):
            continue

        handle = parsed.path.rstrip("/").split("/")[-1]

        if not handle:
            continue

        products.add(url)

    return sorted(products)


def get_product_handle(product_url: str) -> str:
    """
    Extract Shopify product handle.
    """

    path = urlparse(product_url).path.rstrip("/")

    match = re.search(r"/products/([^/]+)", path)

    if not match:
        raise ValueError(
            f"Could not extract product handle from: {product_url}"
        )

    return match.group(1)


def fetch_product_json(product_url: str) -> dict:
    """
    Fetch the Shopify product JSON endpoint.

    Example:
        /products/dry-sift-hash
        ->
        /products/dry-sift-hash.js
    """

    handle = get_product_handle(product_url)

    endpoint = f"{BASE_URL}/products/{handle}.js"

    print(f"    Product: {handle}")

    response = session.get(
        endpoint,
        headers={
            **HEADERS,
            "Accept": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(
            f"Unexpected product response for {product_url}"
        )

    return data


def normalize_price(value):
    """
    Shopify normally returns prices in cents.
    """

    if value is None:
        return None

    try:
        return round(float(value) / 100, 2)
    except (TypeError, ValueError):
        return value


def normalize_product(product: dict, product_url: str) -> dict:
    """
    Convert Shopify's product JSON into the structure
    we want to store.
    """

    variants = []

    for variant in product.get("variants", []):
        featured_image = variant.get("featured_image")

        if isinstance(featured_image, dict):
            featured_image = featured_image.get("src")

        variants.append(
            {
                "id": variant.get("id"),
                "title": variant.get("title"),
                "sku": variant.get("sku"),
                "available": variant.get("available"),
                "price": normalize_price(
                    variant.get("price")
                ),
                "compare_at_price": normalize_price(
                    variant.get("compare_at_price")
                ),
                "option1": variant.get("option1"),
                "option2": variant.get("option2"),
                "option3": variant.get("option3"),
                "featured_image": featured_image,
            }
        )

    images = []

    for image in product.get("images", []):
        if isinstance(image, dict):
            image = image.get("src")

        if image:
            images.append(image)

    return {
        "id": product.get("id"),
        "title": product.get("title"),
        "handle": product.get("handle"),
        "url": product_url,
        "description": product.get("description"),
        "vendor": product.get("vendor"),
        "product_type": product.get("type"),
        "tags": product.get("tags", []),
        "available": product.get("available"),
        "price": normalize_price(product.get("price")),
        "compare_at_price": normalize_price(
            product.get("compare_at_price")
        ),
        "featured_image": product.get("featured_image"),
        "images": images,
        "options": product.get("options", []),
        "variants": variants,
    }


def scrape():
    """
    Main scraper.
    """

    collections = get_collection_links()

    print()
    print(f"Found {len(collections)} collections")
    print()

    result = {}

    product_cache = {}

    for collection in collections:

        collection_handle = collection["handle"]

        collection_title = collection["title"]

        collection_url = collection["url"]

        print(
            f"\n=== {collection_title} "
            f"({collection_handle}) ==="
        )

        product_urls = get_product_links(
            collection_url
        )

        print(
            f"  Found {len(product_urls)} products"
        )

        products = []

        for product_url in product_urls:

            if product_url in product_cache:
                product = product_cache[product_url]

            else:
                try:
                    raw_product = fetch_product_json(
                        product_url
                    )

                    product = normalize_product(
                        raw_product,
                        product_url,
                    )

                    product_cache[product_url] = product

                except Exception as error:
                    print(
                        f"    ERROR: {product_url}"
                    )
                    print(
                        f"    {error}"
                    )
                    continue

                # Small delay between requests.
                time.sleep(0.25)

            products.append(product)

        result[collection_handle] = {
            "title": collection_title,
            "url": collection_url,
            "product_count": len(products),
            "products": products,
        }

    return result


def main():
    data = scrape()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Saved to: {OUTPUT_FILE}")

    total_products = sum(
        collection["product_count"]
        for collection in data.values()
    )

    print(f"Collections: {len(data)}")
    print(f"Products: {total_products}")


if __name__ == "__main__":
    main()