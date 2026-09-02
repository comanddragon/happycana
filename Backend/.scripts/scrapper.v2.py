import json
import re
import time
from pathlib import Path

import requests

VENUE_ID = "145c714690909516"

HEADERS = {
    "api-key": "49dac8e0-7743-11e9-8e3f-a5601eb2e936",
    "origin": "https://happydaysli.com",
    "referer": "https://happydaysli.com/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
}

LIMIT = 100
OUTPUT_DIR = Path("output/categories")
OUTPUT_DIR.mkdir(exist_ok=True)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def fetch_page(category_id, skip):
    url = (
        f"https://api.dispenseapp.com/v1/venues/"
        f"{VENUE_ID}/product-categories/{category_id}/products"
    )

    params = {
        "skip": skip,
        "limit": LIMIT,
        "orderPickUpType": "IN_STORE",
    }

    r = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    r.raise_for_status()
    return r.json()


def extract_products(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("products", "data", "items", "results"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def fetch_category_products(category):
    category_id = category["_id"]

    all_products = []
    skip = 0

    while True:
        data = fetch_page(category_id, skip)
        products = extract_products(data)

        if not products:
            break

        all_products.extend(products)

        if len(products) < LIMIT:
            break

        skip += LIMIT
        time.sleep(0.5)

    return all_products


def safe_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return (
            value.get("name")
            or value.get("label")
            or value.get("title")
            or json.dumps(value, sort_keys=True)
        )

    if isinstance(value, list):
        return ", ".join(str(v) for v in value)

    return str(value)


def analyse_products(products):
    brands = set()
    categories = set()
    product_types = set()
    sub_types = set()
    cannabis_types = set()
    terpene_types = set()

    for p in products:

        brand = safe_value(p.get("brand"))
        if brand:
            brands.add(brand)

        category = safe_value(p.get("category"))
        if category:
            categories.add(category)

        ptype = safe_value(p.get("type"))
        if ptype:
            product_types.add(ptype)

        subtype = safe_value(p.get("subType"))
        if subtype:
            sub_types.add(subtype)

        cannabis_type = safe_value(p.get("cannabisType"))
        if cannabis_type:
            cannabis_types.add(cannabis_type)

        terpene = safe_value(p.get("terpeneType"))
        if terpene:
            terpene_types.add(terpene)

    return {
        "product_count": len(products),
        "brands": sorted(brands),
        "categories": sorted(categories),
        "types": sorted(product_types),
        "sub_types": sorted(sub_types),
        "cannabis_types": sorted(cannabis_types),
        "terpene_types": sorted(terpene_types),
    }
    brands = set()
    categories = set()
    product_types = set()
    sub_types = set()
    cannabis_types = set()
    terpene_types = set()

    for p in products:

        brand = p.get("brand")
        if brand:
            if isinstance(brand, dict):
                print("BRAND IS DICT:")
                print(json.dumps(brand, indent=2)) 
            brands.add(brand)

        category = p.get("category")
        if category:
            categories.add(str(category))

        ptype = p.get("type")
        if ptype:
            product_types.add(str(ptype))

        subtype = p.get("subType")
        if subtype:
            sub_types.add(str(subtype))

        cannabis_type = p.get("cannabisType")
        if cannabis_type:
            cannabis_types.add(str(cannabis_type))

        terpene = p.get("terpeneType")
        if terpene:
            terpene_types.add(str(terpene))

    return {
        "product_count": len(products),
        "brands": sorted(brands),
        "categories": sorted(categories),
        "types": sorted(product_types),
        "sub_types": sorted(sub_types),
        "cannabis_types": sorted(cannabis_types),
        "terpene_types": sorted(terpene_types),
    }


def main():
    with open("categories.json", "r", encoding="utf-8") as f:
        categories = json.load(f)

    category_analysis = {}

    for category in categories:

        category_name = category["name"]
        category_id = category["_id"]

        print(f"\nFetching: {category_name}")
        print(f"Category ID: {category_id}")

        products = fetch_category_products(category)

        filename = slugify(category.get("slug") or category_name)
        filepath = OUTPUT_DIR / f"{filename}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        category_analysis[filename] = analyse_products(products)

        print(f"Saved {len(products)} products")

    with open(
        OUTPUT_DIR / "category_analysis.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            category_analysis,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nFinished")


if __name__ == "__main__":
    main()