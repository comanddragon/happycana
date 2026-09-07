#!/usr/bin/env python3
"""
PeptidesDirect catalog scraper.

Scrapes the public PeptidesDirect catalog without authentication.

Source:
    https://peptidesdirect.com/shop/

The site uses a custom storefront rather than WooCommerce, so this scraper
does NOT depend on WooCommerce selectors.

It discovers category links from the shop page, extracts product cards from
the rendered HTML/text, then visits each product page to collect additional
metadata.

Outputs:
    products.csv
    categories.csv

The scraper is resumable: products already present in products.csv are
loaded and merged with newly discovered products.
"""

import argparse
import csv
import hashlib
import random
import re
import time
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunsplit

import requests
from bs4 import BeautifulSoup


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]

DEFAULT_OUTPUT = (
    BACKEND_DIR
    / ".output"
    / "peptides"
    / "products"
    / "products.csv"
)

DEFAULT_CATEGORIES_OUTPUT = (
    BACKEND_DIR
    / ".output"
    / "peptides"
    / "categories"
    / "categories.csv"
)

BASE_URL = "https://peptidesdirect.com"
SHOP_URL = f"{BASE_URL}/shop"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)

MAX_RETRIES = 5
BACKOFF_SECONDS = 2.0


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ScrapedProduct:
    source_url: str
    name: str
    price: Decimal | None = None
    compare_at_price: Decimal | None = None
    categories: list[str] = field(default_factory=list)
    image_url: str = ""
    meta_title: str = ""
    meta_description: str = ""
    short_description: str = ""
    sku: str = ""
    cas_number: str = ""
    molecular_weight: str = ""
    purity: str = ""
    strength: str = ""

    @property
    def source_id(self):
        return (
            "peptide:"
            + hashlib.sha256(self.source_url.encode()).hexdigest()[:32]
        )

    def to_row(self):
        profile = infer_profile(self.name, self.strength)

        return {
            "source_id": self.source_id,
            **asdict(self),
            "price": str(self.price) if self.price is not None else "",
            "compare_at_price": (
                str(self.compare_at_price)
                if self.compare_at_price is not None
                else ""
            ),
            "categories": "|".join(self.categories),
            **profile,
        }


@dataclass
class CategoryStat:
    name: str
    url: str
    scraped_count: int
    reported_count: int | None = None

    def to_row(self):
        return {
            "name": self.name,
            "url": self.url,
            "scraped_count": self.scraped_count,
            "reported_count": (
                self.reported_count
                if self.reported_count is not None
                else ""
            ),
        }


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def build_session():
    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,image/webp,"
            "*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })

    return session


def get(session, url):
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                timeout=30,
                allow_redirects=True,
            )

            if response.status_code == 200:
                return response

            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt == MAX_RETRIES:
                    response.raise_for_status()

                wait = min(
                    BACKOFF_SECONDS * (2 ** attempt),
                    60,
                ) + random.uniform(0.2, 1.0)

                print(
                    f"  HTTP {response.status_code}; "
                    f"retrying in {wait:.1f}s "
                    f"({attempt + 1}/{MAX_RETRIES})"
                )

                time.sleep(wait)
                continue

            response.raise_for_status()

        except (
            requests.Timeout,
            requests.ConnectionError,
        ) as exc:
            if attempt == MAX_RETRIES:
                raise

            wait = min(
                BACKOFF_SECONDS * (2 ** attempt),
                60,
            ) + random.uniform(0.2, 1.0)

            print(
                f"  Network error: {exc}; "
                f"retrying in {wait:.1f}s "
                f"({attempt + 1}/{MAX_RETRIES})"
            )

            time.sleep(wait)

    raise RuntimeError(f"Unable to fetch {url}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_url(url):
    if not url:
        return ""

    parsed = urlparse(url)

    return urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip("/") or "/",
        parsed.query,
        "",
    ))


def normalize_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_price(text):
    if not text:
        return None

    matches = re.findall(
        r"(?:USD\s*)?\$?\s*"
        r"([0-9][0-9,]*(?:\.\d{1,2})?)",
        text,
        re.I,
    )

    if not matches:
        return None

    try:
        return Decimal(matches[-1].replace(",", ""))
    except InvalidOperation:
        return None


def extract_price_from_text(text):
    if not text:
        return None

    # Prefer explicit dollar amounts.
    matches = re.findall(
        r"\$\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
        text,
    )

    if matches:
        try:
            return Decimal(matches[0].replace(",", ""))
        except InvalidOperation:
            pass

    # "From $89"
    match = re.search(
        r"\bfrom\s+\$?\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
        text,
        re.I,
    )

    if match:
        try:
            return Decimal(match.group(1).replace(",", ""))
        except InvalidOperation:
            pass

    return None


def extract_strength(text):
    if not text:
        return ""

    patterns = [
        r"\b\d+(?:\.\d+)?\s*mg\b",
        r"\b\d+(?:\.\d+)?\s*mcg\b",
        r"\b\d+(?:\.\d+)?\s*µg\b",
        r"\b\d+(?:\.\d+)?\s*IU\b",
        r"\b\d+(?:\.\d+)?\s*g\b",
    ]

    values = []

    for pattern in patterns:
        values.extend(
            re.findall(pattern, text, re.I)
        )

    if not values:
        return ""

    # Preserve unique strengths in the order found.
    seen = set()
    result = []

    for value in values:
        value = normalize_text(value)

        if value.lower() not in seen:
            seen.add(value.lower())
            result.append(value)

    return " · ".join(result)


def infer_profile(name, strength=""):
    lowered = name.lower()

    if "capsule" in lowered:
        form = "Capsules"
    elif "tablet" in lowered:
        form = "Tablets"
    elif "topical" in lowered:
        form = "Topical"
    elif "blend" in lowered:
        form = "Lyophilized blend"
    else:
        form = "Lyophilized powder"

    concentration = strength

    if not concentration:
        match = re.search(
            r"\b(\d+(?:\.\d+)?\s*(?:mcg|mg|ml|iu|g))\b",
            name,
            re.I,
        )

        if match:
            concentration = (
                match.group(1)
                .replace(" ", "")
            )

    return {
        "concentration": concentration,
        "form": form,
        "storage_requirements": (
            "Store according to supplier documentation. "
            "Research use only."
        ),
    }


# ---------------------------------------------------------------------------
# Category discovery
# ---------------------------------------------------------------------------

def discover_categories(html, base_url):
    """
    Discover categories from links such as:

        /shop?cat=GLP-1+%26+Metabolic

    Also accepts normal /shop?cat=... links whose display text is the
    category name.
    """

    soup = BeautifulSoup(html, "html.parser")

    categories = []
    seen = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        text = normalize_text(anchor.get_text(" ", strip=True))

        if not href:
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        if parsed.netloc.lower() != urlparse(BASE_URL).netloc.lower():
            continue

        if parsed.path.rstrip("/") != "/shop":
            continue

        query = dict(parse_qsl(parsed.query))

        category = query.get("cat")

        if not category:
            continue

        category = normalize_text(category)

        if not category:
            continue

        if category.lower() in {"all", "all peptides"}:
            continue

        key = category.lower()

        if key in seen:
            continue

        seen.add(key)

        categories.append({
            "name": category,
            "url": clean_url(absolute),
        })

    return categories


# ---------------------------------------------------------------------------
# Product URL discovery
# ---------------------------------------------------------------------------

def is_product_url(url):
    parsed = urlparse(url)

    if parsed.netloc.lower() != urlparse(BASE_URL).netloc.lower():
        return False

    path = parsed.path.rstrip("/")

    return bool(
        re.match(
            r"^/product/[^/]+$",
            path,
            re.I,
        )
    )


def discover_product_urls(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    found = []
    seen = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")

        if not href:
            continue

        absolute = clean_url(
            urljoin(base_url, href)
        )

        if not is_product_url(absolute):
            continue

        if absolute in seen:
            continue

        seen.add(absolute)
        found.append(absolute)

    return found


# ---------------------------------------------------------------------------
# Product card parsing
# ---------------------------------------------------------------------------

def find_product_card(anchor):
    """
    Walk upward looking for a useful product-card container.

    PeptidesDirect isn't WooCommerce, so don't depend on a specific CSS class.
    """

    current = anchor

    for _ in range(8):
        if current is None:
            break

        text = normalize_text(
            current.get_text(" ", strip=True)
        )

        if (
            "$" in text
            and len(text) < 2500
        ):
            return current

        current = current.parent

    return anchor.parent


def parse_product_cards(html, source_url, category=None):
    soup = BeautifulSoup(html, "html.parser")

    products = []
    seen = set()

    anchors = soup.select("a[href]")

    for anchor in anchors:
        href = anchor.get("href", "")

        absolute = clean_url(
            urljoin(source_url, href)
        )

        if not is_product_url(absolute):
            continue

        if absolute in seen:
            continue

        card = find_product_card(anchor)

        card_text = normalize_text(
            card.get_text(" ", strip=True)
        )

        # Product names are usually headings, strong text, or the
        # visible anchor itself.
        title_node = (
            card.select_one(
                "h2, h3, h4, h5, "
                "[class*='title'], "
                "[class*='name']"
            )
        )

        name = (
            normalize_text(
                title_node.get_text(" ", strip=True)
            )
            if title_node
            else normalize_text(
                anchor.get_text(" ", strip=True)
            )
        )

        if not name:
            continue

        # Avoid treating navigation links as products.
        if len(name) > 180:
            continue

        price = extract_price_from_text(card_text)

        strength = extract_strength(card_text)

        image_url = ""

        image = card.select_one("img")

        if image:
            image_url = (
                image.get("src")
                or image.get("data-src")
                or image.get("data-lazy-src")
                or ""
            )

            if image_url:
                image_url = urljoin(
                    source_url,
                    image_url,
                )

        description = ""

        # Prefer a paragraph that isn't simply the price/CTA.
        for node in card.select("p, div, span"):
            value = normalize_text(
                node.get_text(" ", strip=True)
            )

            if (
                value
                and value != name
                and "$" not in value
                and "add to cart" not in value.lower()
                and "deep dive" not in value.lower()
                and len(value) >= 25
                and len(value) <= 500
            ):
                description = value
                break

        products.append(
            ScrapedProduct(
                source_url=absolute,
                name=name,
                price=price,
                categories=[category] if category else [],
                image_url=image_url,
                short_description=description,
                strength=strength,
            )
        )

        seen.add(absolute)

    return products


# ---------------------------------------------------------------------------
# Product detail parsing
# ---------------------------------------------------------------------------

def parse_product_detail(html, product):
    soup = BeautifulSoup(html, "html.parser")

    # SEO title.
    title = soup.select_one("title")

    if title:
        product.meta_title = normalize_text(
            title.get_text(" ", strip=True)
        )

    # SEO description.
    description = (
        soup.select_one(
            'meta[name="description"]'
        )
        or soup.select_one(
            'meta[property="og:description"]'
        )
    )

    if description:
        product.meta_description = normalize_text(
            description.get("content", "")
        )

    # OpenGraph image is often more reliable than the product-card image.
    og_image = soup.select_one(
        'meta[property="og:image"]'
    )

    if og_image and og_image.get("content"):
        product.image_url = urljoin(
            product.source_url,
            og_image["content"],
        )

    text = normalize_text(
        soup.get_text(" ", strip=True)
    )

    # SKU.
    sku_match = re.search(
        r"\b(?:SKU|Product\s*(?:Code|ID))"
        r"\s*[:#]?\s*([A-Z0-9._-]+)",
        text,
        re.I,
    )

    if sku_match:
        product.sku = sku_match.group(1)

    # CAS.
    cas_match = re.search(
        r"\bCAS\b\s*[:#]?\s*"
        r"(\d{2,7}-\d{2}-\d)",
        text,
        re.I,
    )

    if cas_match:
        product.cas_number = cas_match.group(1)

    # Molecular weight.
    mw_match = re.search(
        r"\b(?:MW|Molecular\s+Weight)\b"
        r"\s*[:#]?\s*"
        r"([0-9]+(?:\.[0-9]+)?)\s*g?/mol",
        text,
        re.I,
    )

    if mw_match:
        product.molecular_weight = (
            mw_match.group(1) + " g/mol"
        )

    # Purity.
    purity_match = re.search(
        r"\b(?:Purity)\b"
        r"\s*[:#]?\s*"
        r"(≥\s*)?([0-9]+(?:\.[0-9]+)?)\s*%",
        text,
        re.I,
    )

    if purity_match:
        prefix = purity_match.group(1) or ""
        product.purity = (
            f"{prefix}{purity_match.group(2)}%"
        )

    # Strength.
    if not product.strength:
        product.strength = extract_strength(text)

    # Try to find a more useful description.
    if not product.short_description:
        paragraphs = [
            normalize_text(p.get_text(" ", strip=True))
            for p in soup.select("p")
        ]

        for paragraph in paragraphs:
            if (
                len(paragraph) >= 40
                and len(paragraph) <= 1200
                and "$" not in paragraph
                and "research use only" not in paragraph.lower()
            ):
                product.short_description = paragraph
                break

    # Product page may contain a better price than the card.
    if product.price is None:
        product.price = extract_price_from_text(text)

    return product


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_shop(
    session,
    shop_url,
    delay,
    items,
    on_products_saved=None,
):
    print(f"Fetching PeptidesDirect shop: {shop_url}")

    response = get(session, shop_url)

    html = response.text

    if len(html) < 3000:
        print(
            f"  WARNING: shop response is unusually small "
            f"({len(html)} bytes)"
        )

    product_urls = discover_product_urls(
        html,
        shop_url,
    )

    print(
        f"  Main shop: {len(product_urls)} product links found"
    )

    parsed_products = parse_product_cards(
        html,
        shop_url,
    )

    print(
        f"  Main shop: {len(parsed_products)} products parsed"
    )

    merge_products(
        items,
        parsed_products,
    )

    if on_products_saved:
        on_products_saved()

    categories = discover_categories(
        html,
        shop_url,
    )

    print(
        f"  Categories discovered: {len(categories)}"
    )

    category_stats = []

    for category_index, category in enumerate(
        categories,
        1,
    ):
        print()
        print(
            f"[{category_index}/{len(categories)}] "
            f"Category: {category['name']}"
        )

        category_response = get(
            session,
            category["url"],
        )

        category_html = category_response.text

        category_products = parse_product_cards(
            category_html,
            category["url"],
            category["name"],
        )

        category_urls = discover_product_urls(
            category_html,
            category["url"],
        )

        print(
            f"  Product links: {len(category_urls)}"
        )

        print(
            f"  Products parsed: {len(category_products)}"
        )

        merge_products(
            items,
            category_products,
        )

        if on_products_saved:
            on_products_saved()

        # Reported count from:
        # "# products"
        count_match = re.search(
            r"(\d+)\s+products?\b",
            category_html,
            re.I,
        )

        reported_count = (
            int(count_match.group(1))
            if count_match
            else None
        )

        category_stats.append(
            CategoryStat(
                name=category["name"],
                url=category["url"],
                scraped_count=len(category_products),
                reported_count=reported_count,
            )
        )

        if delay:
            time.sleep(delay)

    return category_stats


def merge_products(items, products):
    for product in products:
        existing = items.get(
            product.source_url
        )

        if existing is None:
            items[product.source_url] = product
            continue

        if not existing.name and product.name:
            existing.name = product.name

        if existing.price is None and product.price is not None:
            existing.price = product.price

        if not existing.image_url and product.image_url:
            existing.image_url = product.image_url

        if not existing.short_description and product.short_description:
            existing.short_description = product.short_description

        if not existing.strength and product.strength:
            existing.strength = product.strength

        for category in product.categories:
            if (
                category
                and category not in existing.categories
            ):
                existing.categories.append(category)


def fetch_product_details(
    session,
    items,
    delay,
    on_saved=None,
):
    products = list(items.values())

    print()
    print(
        f"Fetching product details for {len(products)} products"
    )
    print()

    for index, product in enumerate(
        products,
        1,
    ):
        try:
            print(
                f"  [{index}/{len(products)}] "
                f"{product.name}"
            )

            response = get(
                session,
                product.source_url,
            )

            parse_product_detail(
                response.text,
                product,
            )

            print(
                f"      price: "
                f"{product.price if product.price is not None else 'not found'}"
            )

            print(
                f"      category: "
                f"{', '.join(product.categories) or 'none'}"
            )

            if product.cas_number:
                print(
                    f"      CAS: {product.cas_number}"
                )

            if product.purity:
                print(
                    f"      purity: {product.purity}"
                )

        except (
            requests.RequestException,
            RuntimeError,
        ) as exc:
            print(
                f"      FAILED: {exc}"
            )

        if on_saved:
            on_saved()

        if (
            delay
            and index < len(products)
        ):
            time.sleep(delay)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def write_csv(items, output):
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "source_id",
        "source_url",
        "name",
        "price",
        "compare_at_price",
        "categories",
        "image_url",
        "meta_title",
        "meta_description",
        "short_description",
        "sku",
        "cas_number",
        "molecular_weight",
        "purity",
        "strength",
        "concentration",
        "form",
        "storage_requirements",
    ]

    temporary = output.with_suffix(
        output.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            item.to_row()
            for item in items
        )

    temporary.replace(output)


def write_categories_csv(
    category_stats,
    output,
):
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "name",
        "url",
        "scraped_count",
        "reported_count",
    ]

    temporary = output.with_suffix(
        output.suffix + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            stat.to_row()
            for stat in category_stats
        )

    temporary.replace(output)


def as_decimal(value):
    if value in (None, ""):
        return None

    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def read_products_csv(path):
    if not path.exists():
        return {}

    items = {}

    with path.open(
        encoding="utf-8",
        newline="",
    ) as file:
        for row in csv.DictReader(file):
            source_url = row.get(
                "source_url"
            )

            if not source_url:
                continue

            categories = [
                value
                for value in (
                    row.get("categories") or ""
                ).split("|")
                if value
            ]

            items[source_url] = ScrapedProduct(
                source_url=source_url,
                name=row.get("name", ""),
                price=as_decimal(
                    row.get("price")
                ),
                compare_at_price=as_decimal(
                    row.get("compare_at_price")
                ),
                categories=categories,
                image_url=row.get(
                    "image_url",
                    "",
                ),
                meta_title=row.get(
                    "meta_title",
                    "",
                ),
                meta_description=row.get(
                    "meta_description",
                    "",
                ),
                short_description=row.get(
                    "short_description",
                    "",
                ),
                sku=row.get(
                    "sku",
                    "",
                ),
                cas_number=row.get(
                    "cas_number",
                    "",
                ),
                molecular_weight=row.get(
                    "molecular_weight",
                    "",
                ),
                purity=row.get(
                    "purity",
                    "",
                ),
                strength=row.get(
                    "strength",
                    "",
                ),
            )

    return items


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--source-url",
        default=SHOP_URL,
        help=(
            "PeptidesDirect shop URL "
            f"(default: {SHOP_URL})"
        ),
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--categories-output",
        type=Path,
        default=DEFAULT_CATEGORIES_OUTPUT,
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
        help=(
            "Ignore existing products.csv"
        ),
    )

    args = parser.parse_args()

    output = args.output.resolve()

    categories_output = (
        args.categories_output.resolve()
    )

    print("=" * 60)
    print("PeptidesDirect Catalog Scraper")
    print("=" * 60)

    print(
        f"Source:            {args.source_url}"
    )

    print(
        f"Products output:   {output}"
    )

    print(
        f"Categories output: {categories_output}"
    )

    if args.no_resume:
        items = {}
    else:
        items = read_products_csv(
            output
        )

    print(
        f"Existing products loaded from disk: "
        f"{len(items)}"
    )

    print()

    session = build_session()

    def save_products():
        write_csv(
            list(items.values()),
            output,
        )

    category_stats = scrape_shop(
        session=session,
        shop_url=args.source_url,
        delay=max(0, args.delay),
        items=items,
        on_products_saved=save_products,
    )

    print()

    if not items:
        raise SystemExit(
            "No products found. "
            "PeptidesDirect may have changed its storefront "
            "or returned a challenge page."
        )

    fetch_product_details(
        session=session,
        items=items,
        delay=max(0, args.delay),
        on_saved=save_products,
    )

    save_products()

    write_categories_csv(
        category_stats,
        categories_output,
    )

    print()
    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)

    print(
        f"Total products saved: "
        f"{len(items)}"
    )

    print(
        f"Total categories saved: "
        f"{len(category_stats)}"
    )

    print(
        f"Products file:   {output}"
    )

    print(
        f"Categories file: {categories_output}"
    )


if __name__ == "__main__":
    main()
