import json
import time
import requests

API_URL = (
    "https://api.dispenseapp.com/v1/venues/"
    "145c714690909516/product-categories/"
    "dfcc77617891f91c/products"
)


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


def fetch_page(skip):
    params = {
        "skip": skip,
        "limit": LIMIT,
        "orderPickUpType": "IN_STORE",
    }

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def extract_products(data):
    """
    Adjust this if the API response structure differs.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["products", "data", "items", "results"]:
            if key in data and isinstance(data[key], list):
                return data[key]

    return []


def main():
    all_products = []
    skip = 0

    while True:
        print(f"Fetching products starting at {skip}...")

        data = fetch_page(skip)
        products = extract_products(data)

        if not products:
            print("No more products found.")
            break

        all_products.extend(products)
        print(f"Retrieved {len(products)} products")

        if len(products) < LIMIT:
            break

        skip += LIMIT
        time.sleep(0.5)

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_products)} products to products.json")


if __name__ == "__main__":
    main()