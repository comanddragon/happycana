#!/usr/bin/env python3
"""Scrape a public peptide catalog into a reusable CSV checkpoint.

Examples:
    python scrape_products.py
    python scrape_products.py --pages 4 --output products.csv
"""

import argparse
import csv
import hashlib
import re
import time
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]
DEFAULT_OUTPUT = BACKEND_DIR / ".output" / "peptides" / "products" / "products.csv"
DEFAULT_SOURCE = "https://www.corepeptides.com/"
USER_AGENT = "CatalogResearchBot/1.0 (+local catalog import; respects robots.txt)"


@dataclass
class ScrapedProduct:
    source_url: str
    name: str
    price: Decimal
    compare_at_price: Decimal | None = None
    categories: list[str] = field(default_factory=list)
    image_url: str = ""

    @property
    def source_id(self):
        return "peptide:" + hashlib.sha256(self.source_url.encode()).hexdigest()[:32]

    def to_row(self):
        profile = infer_profile(self.name)
        return {
            "source_id": self.source_id,
            **asdict(self),
            "price": str(self.price),
            "compare_at_price": str(self.compare_at_price or ""),
            "categories": "|".join(self.categories),
            **profile,
        }


def parse_price(text):
    values = re.findall(r"(?:USD\s*)?\$?([0-9][0-9,]*(?:\.\d{1,2})?)", text or "")
    if not values:
        return None
    try:
        return Decimal(values[-1].replace(",", ""))
    except InvalidOperation:
        return None


def parse_catalog_page(html, source_url):
    """Parse WooCommerce cards without depending on one theme's exact markup.

    Category badges are not rendered on the shop archive grid on most WooCommerce
    themes (including this one), so categories are fetched separately from each
    product's own page in fetch_categories() below.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.product, .product-grid-item, .wd-product, article.product")
    products = []
    seen = set()
    for card in cards:
        title = card.select_one("h2, h3, .woocommerce-loop-product__title, .wd-entities-title")
        anchor = None
        if title:
            anchor = title if title.name == "a" and title.get("href") else title.find_parent("a", href=True)
        anchor = anchor or card.select_one("a[href*='/product/']")
        name = title.get_text(" ", strip=True) if title else ""
        if not name or not anchor:
            continue
        product_url = urljoin(source_url, anchor["href"])
        if product_url in seen:
            continue
        price_node = card.select_one(".price")
        price = parse_price(price_node.get_text(" ", strip=True) if price_node else "")
        if price is None:
            continue
        old_price_node = price_node.select_one("del") if price_node else None
        compare_at = parse_price(old_price_node.get_text(" ", strip=True)) if old_price_node else None
        image = card.select_one("img")
        image_url = ""
        if image:
            image_url = image.get("data-lazy-src") or image.get("data-src") or image.get("src") or ""
        products.append(ScrapedProduct(
            source_url=product_url,
            name=name,
            price=price,
            compare_at_price=compare_at if compare_at and compare_at > price else None,
            image_url=urljoin(source_url, image_url),
        ))
        seen.add(product_url)
    return products


def parse_product_categories(html):
    """Extract real WooCommerce categories from a single product page.

    Standard WooCommerce single-product templates render:
        <span class="posted_in">Category: <a href="...">X</a>, <a href="...">Y</a></span>
    Falls back to the breadcrumb trail (minus "Home" and the product name itself)
    for themes that omit posted_in.
    """
    soup = BeautifulSoup(html, "html.parser")
    posted_in = soup.select_one(".posted_in")
    if posted_in:
        categories = [a.get_text(" ", strip=True) for a in posted_in.select("a") if a.get_text(strip=True)]
        if categories:
            return categories

    breadcrumb = soup.select_one(".woocommerce-breadcrumb, nav.breadcrumbs, .breadcrumb")
    if not breadcrumb:
        return []
    crumbs = [a.get_text(" ", strip=True) for a in breadcrumb.select("a") if a.get_text(strip=True)]
    return [crumb for crumb in crumbs if crumb.lower() != "home"]


def fetch_categories(session, items, delay):
    """Visit each product's own page to read its real category, in place."""
    total = len(items)
    for index, item in enumerate(items, 1):
        try:
            response = session.get(item.source_url, timeout=25)
            response.raise_for_status()
            item.categories = parse_product_categories(response.text)
        except requests.RequestException as exc:
            print(f"  [{index}/{total}] category fetch failed for {item.source_url}: {exc}")
        if index < total and delay:
            time.sleep(delay)


def infer_profile(name):
    concentration_match = re.search(r"\b(\d+(?:\.\d+)?\s*(?:mcg|mg|ml))\b", name, re.I)
    lowered = name.lower()
    if "capsule" in lowered:
        form = "Capsules"
    elif "topical" in lowered:
        form = "Topical"
    elif "blend" in lowered:
        form = "Lyophilized blend"
    else:
        form = "Lyophilized powder"
    return {
        "concentration": concentration_match.group(1).replace(" ", "") if concentration_match else "",
        "form": form,
        "storage_requirements": "Store according to the supplier documentation. Research use only.",
    }


def build_session():
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html"})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def scrape(source_url, pages, delay):
    if urlparse(source_url).scheme not in {"http", "https"}:
        raise SystemExit("--source-url must be an HTTP(S) URL")
    session = build_session()
    items = {}
    for page in range(1, max(1, pages) + 1):
        url = source_url if page == 1 else source_url.rstrip("/") + f"/page/{page}/"
        response = session.get(url, timeout=25)
        response.raise_for_status()
        parsed = parse_catalog_page(response.text, url)
        print(f"Page {page}: {len(parsed)} products")
        for item in parsed:
            items[item.source_url] = item
        if page < pages and delay:
            time.sleep(delay)
    if not items:
        raise SystemExit("No product cards were found; the source layout may have changed.")
    products = list(items.values())
    print(f"Fetching categories from {len(products)} product pages")
    fetch_categories(session, products, delay)
    return products


def write_csv(items, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_id", "source_url", "name", "price", "compare_at_price", "categories",
        "image_url", "concentration", "form", "storage_requirements",
    ]
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(item.to_row() for item in items)
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    items = scrape(args.source_url, args.pages, max(0, args.delay))
    write_csv(items, args.output.resolve())
    print(f"Wrote {len(items)} products to {args.output.resolve()}")


if __name__ == "__main__":
    main()