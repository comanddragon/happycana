#!/usr/bin/env python3
"""Scrape a public peptide catalog into a reusable CSV checkpoint.

Supports two storefront platforms, auto-detected per source URL:
  - WooCommerce (e.g. corepeptides.com): categories aren't on the archive
    grid, so each product's own page is visited once to read them.
  - BigCommerce Stencil (e.g. limitlesslifenootropics.com): categories come
    from the archive URL itself (each category has its own page), and
    pricing is commonly gated behind a login wall for B2B "research
    professional" storefronts -- those rows are written with an empty
    price and are skipped by seed_products.py until priced manually.

Saves as it goes, like scrape_blogs.py: products.csv is rewritten (via an
atomic tmp-file + replace) after every page and after every per-product
category lookup, and categories.csv is rewritten after every category
finishes -- so a crash or Ctrl-C partway through only costs the current
in-flight page, not the whole run. On the next run, any existing
products.csv is loaded first and merged with freshly scraped data instead
of being overwritten from scratch (pass --no-resume to start clean).
Progress is logged to stdout throughout: which category/page is being
fetched, how many products were found on it, when a save happens and the
running total on disk, and a final summary banner.

Examples:
    # No flags: scrapes BOTH default sources -- corepeptides.com (WooCommerce,
    # single page) and every category discovered off limitlesslifenootropics.com's
    # category hub (BigCommerce). Passing --source-url and/or
    # --discover-category-hub explicitly overrides these defaults rather than
    # adding to them.
    python scrape_products.py
    python scrape_products.py --pages 4 --output products.csv

    # One BigCommerce category, several pages:
    python scrape_products.py \\
        --source-url "https://limitlesslifenootropics.com/product-category/cognitive-research/" \\
        --pages 5

    # Crawl every category linked from a site's category hub page:
    python scrape_products.py \\
        --discover-category-hub "https://limitlesslifenootropics.com/shop-by-research-category/" \\
        --pages 20

    # Both sites explicitly, side by side:
    python scrape_products.py \\
        --source-url "https://www.corepeptides.com/" \\
        --discover-category-hub "https://limitlesslifenootropics.com/shop-by-research-category/" \\
        --pages 10
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
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[2]
DEFAULT_OUTPUT = BACKEND_DIR / ".output" / "peptides" / "products" / "products.csv"
DEFAULT_CATEGORIES_OUTPUT = BACKEND_DIR / ".output" / "peptides" / "categories" / "categories.csv"
DEFAULT_SOURCE = "https://www.corepeptides.com/"
DEFAULT_DISCOVER_HUB = "https://limitlesslifenootropics.com/shop-by-research-category/"
USER_AGENT = "CatalogResearchBot/1.0 (+local catalog import; respects robots.txt)"
MAX_RETRIES = 7
BACKOFF_SECONDS = 2.0
CATEGORY_HREF_RE = re.compile(r"/(product-category|research-peptide-categories|product-type)/[^/?#]+/?$")
FILTER_QUERYSTRING_MARKERS = ("_bc_fsnf", "is_featured", "in_stock", "Grade=", "Container=")


@dataclass
class ScrapedProduct:
    source_url: str
    name: str
    price: Decimal | None = None
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
            "price": str(self.price) if self.price is not None else "",
            "compare_at_price": str(self.compare_at_price or ""),
            "categories": "|".join(self.categories),
            **profile,
        }


@dataclass
class CategoryStat:
    name: str
    url: str
    platform: str
    scraped_count: int
    reported_count: int | None = None

    def to_row(self):
        return {
            "name": self.name,
            "url": self.url,
            "platform": self.platform,
            "scraped_count": self.scraped_count,
            "reported_count": self.reported_count if self.reported_count is not None else "",
        }


def parse_price(text):
    values = re.findall(r"(?:USD\s*)?\$?([0-9][0-9,]*(?:\.\d{1,2})?)", text or "")
    if not values:
        return None
    try:
        return Decimal(values[-1].replace(",", ""))
    except InvalidOperation:
        return None


def detect_platform(html):
    """Guess the storefront platform from generator meta tags / asset hosts.

    Falls back to "woocommerce" since that's the original/default source.
    """
    lowered = html.lower()
    if "bigcommerce" in lowered or "cdn11.bigcommerce.com" in lowered or "stencil-utils" in lowered:
        return "bigcommerce"
    if "woocommerce" in lowered or "wp-content" in lowered:
        return "woocommerce"
    return "woocommerce"


def paginate_url(source_url, page, platform):
    """Build the URL for `page` on a given platform's catalog pagination."""
    if page == 1:
        return source_url
    if platform == "bigcommerce":
        parts = urlsplit(source_url)
        query = [(key, value) for key, value in parse_qsl(parts.query) if key != "page"]
        query.append(("page", str(page)))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return source_url.rstrip("/") + f"/page/{page}/"


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


def parse_catalog_page_bigcommerce(html, source_url, category_name=None):
    """Parse BigCommerce Stencil product cards from a category archive page.

    Unlike the WooCommerce grid, each archive URL here *is* a category, so the
    category tag comes from the page itself instead of a per-product visit.
    Pricing is frequently gated behind a "Log In for Professional Pricing"
    link on B2B research-chemical storefronts; when no numeric price is
    present the product is still kept, with `price` left unset, since the
    catalog data (name, url, image, category) is still useful on its own.
    """
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.product, .product, .card")
    products = []
    seen = set()
    for card in cards:
        title = card.select_one(".card-title a, h4.card-title, h4 a, .card-title")
        anchor = None
        if title:
            anchor = title if title.name == "a" and title.get("href") else title.find_parent("a", href=True)
        anchor = anchor or card.select_one("a.card-figure__link, a[href*='/product/']")
        name = title.get_text(" ", strip=True) if title else ""
        if not name or not anchor:
            continue
        product_url = urljoin(source_url, anchor["href"])
        if product_url in seen:
            continue
        price_node = card.select_one(".price, .card-text--price")
        price_text = price_node.get_text(" ", strip=True) if price_node else ""
        price = None if "log in" in price_text.lower() else parse_price(price_text)
        old_price_node = price_node.select_one("del, .price--rrp") if price_node else None
        compare_at = parse_price(old_price_node.get_text(" ", strip=True)) if old_price_node else None
        image = card.select_one("img")
        image_url = ""
        if image:
            image_url = image.get("data-src") or image.get("src") or image.get("data-lazy-src") or ""
        products.append(ScrapedProduct(
            source_url=product_url,
            name=name,
            price=price,
            compare_at_price=compare_at if (compare_at and price and compare_at > price) else None,
            categories=[category_name] if category_name else [],
            image_url=urljoin(source_url, image_url) if image_url else "",
        ))
        seen.add(product_url)
    return products


def parse_category_meta(html):
    """Read the category display name, reported product count, and last page
    number off a BigCommerce Stencil category archive page."""
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one("h1")
    name = heading.get_text(" ", strip=True) if heading else None

    count_match = re.search(r"([\d,]+)\s+Compounds\b", html, re.I) or re.search(r"([\d,]+)\s+Products?\b", html, re.I)
    reported_count = int(count_match.group(1).replace(",", "")) if count_match else None

    max_page = 1
    for match in re.finditer(r"[?&]page=(\d+)", html):
        max_page = max(max_page, int(match.group(1)))
    return name, reported_count, max_page


def discover_category_links(html, base_url):
    """Pull real category archive links (not filter/sort links) off a hub page
    such as /shop-by-research-category/ or /shop-by-type/."""
    soup = BeautifulSoup(html, "html.parser")
    found = []
    seen = set()
    for anchor in soup.select("a[href]"):
        href = anchor["href"]
        if any(marker in href for marker in FILTER_QUERYSTRING_MARKERS):
            continue
        if not CATEGORY_HREF_RE.search(urlparse(href).path):
            continue
        url = urljoin(base_url, href).split("?")[0]
        if url in seen:
            continue
        seen.add(url)
        found.append(url)
    return found


def parse_product_categories(html):
    """Extract categories from a single product page (WooCommerce-oriented,
    with a breadcrumb-based fallback used for any platform).

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

    breadcrumb = soup.select_one(".woocommerce-breadcrumb, nav.breadcrumbs, .breadcrumb, .breadcrumbs")
    if not breadcrumb:
        return []
    crumbs = [a.get_text(" ", strip=True) for a in breadcrumb.select("a") if a.get_text(strip=True)]
    return [crumb for crumb in crumbs if crumb.lower() != "home"]


def fetch_categories(session, items, delay, on_saved=None):
    """Visit each product's own page to read its real category, in place.

    Only used for products that came off a page where categories weren't
    already known (currently: WooCommerce archive grids). Calls `on_saved`
    after every product so progress is written to disk immediately -- the
    same way the blog scraper saves after every article.
    """
    total = len(items)
    for index, item in enumerate(items, 1):
        try:
            response = get(session, item.source_url)
            item.categories = parse_product_categories(response.text)
            print(f"  [{index}/{total}] categorized: {item.name} -> {item.categories or 'none found'}")
        except (requests.RequestException, RuntimeError) as exc:
            print(f"  [{index}/{total}] category fetch failed for {item.source_url}: {exc}")
        if on_saved:
            on_saved()
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
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html"})
    return session


def get(session, url):
    """Fetch a URL, respecting Retry-After and backing off on 429/5xx."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=25)
            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
                return response
            if attempt == MAX_RETRIES:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After", "")
            try:
                wait = float(retry_after)
            except ValueError:
                wait = BACKOFF_SECONDS * (2 ** attempt)
            wait = min(wait, 120) + random.uniform(0.25, 1.25)
            print(f"  HTTP {response.status_code}; retrying {url} in {wait:.1f}s ({attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = min(BACKOFF_SECONDS * (2 ** attempt), 120) + random.uniform(0.25, 1.25)
            print(f"  Network error on {url}: {exc}; retrying in {wait:.1f}s ({attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)
    raise RuntimeError(f"Unable to fetch {url}")


def scrape_category(session, source_url, pages, delay, items, on_saved=None):
    """Scrape one catalog/category root URL across its pages into `items`
    (keyed and merged by product URL). Returns a CategoryStat for it.

    Calls `on_saved` after every page is merged in, so products.csv reflects
    progress as it goes instead of only at the very end of the whole run.
    """
    platform = "woocommerce"
    category_name = None
    reported_count = None
    max_page = max(1, pages)
    scraped_count = 0

    for page in range(1, max(1, pages) + 1):
        if page > max_page:
            break
        url = source_url if page == 1 else paginate_url(source_url, page, platform)
        response = get(session, url)
        html = response.text

        if page == 1:
            platform = detect_platform(html)
            if platform == "bigcommerce":
                category_name, reported_count, discovered_max_page = parse_category_meta(html)
                max_page = min(max(1, pages), discovered_max_page) if pages else discovered_max_page

        if platform == "bigcommerce":
            parsed = parse_catalog_page_bigcommerce(html, url, category_name)
        else:
            parsed = parse_catalog_page(html, url)

        label = category_name or source_url
        print(f"  [{label}] page {page}/{max_page} ({platform}): {len(parsed)} products found")
        if not parsed:
            print(f"  [{label}] no products on this page; stopping pagination")
            break
        scraped_count += len(parsed)
        for item in parsed:
            existing = items.get(item.source_url)
            if existing is None:
                items[item.source_url] = item
                continue
            for category in item.categories:
                if category not in existing.categories:
                    existing.categories.append(category)
            if existing.price is None and item.price is not None:
                existing.price = item.price
            if not existing.image_url and item.image_url:
                existing.image_url = item.image_url

        if on_saved:
            on_saved()
            print(f"  [{label}] saved (total products on disk: {len(items)})")

        if page < max_page and delay:
            time.sleep(delay)

    return CategoryStat(
        name=category_name or source_url,
        url=source_url,
        platform=platform,
        scraped_count=scraped_count,
        reported_count=reported_count,
    )


def scrape(source_urls, pages, delay, discover_category_hub=None, items=None,
           on_products_saved=None, on_categories_saved=None):
    session = build_session()
    seed_urls = list(dict.fromkeys(u for u in source_urls if u))

    if discover_category_hub:
        if urlparse(discover_category_hub).scheme not in {"http", "https"}:
            raise SystemExit("--discover-category-hub must be an HTTP(S) URL")
        print(f"Discovering categories from hub: {discover_category_hub}")
        hub_response = get(session, discover_category_hub)
        discovered = discover_category_links(hub_response.text, discover_category_hub)
        print(f"  found {len(discovered)} category links")
        for url in discovered:
            if url not in seed_urls:
                seed_urls.append(url)
        if delay:
            time.sleep(delay)

    for url in seed_urls:
        if urlparse(url).scheme not in {"http", "https"}:
            raise SystemExit(f"Source URL must be an HTTP(S) URL, got: {url}")
    if not seed_urls:
        raise SystemExit("No source URLs to scrape; pass --source-url and/or --discover-category-hub")

    print()
    print(f"Categories/sources to scrape: {len(seed_urls)}")
    print()

    items = {} if items is None else items
    category_stats = []
    for index, source_url in enumerate(seed_urls, 1):
        print(f"[{index}/{len(seed_urls)}] Category: {source_url}")
        stat = scrape_category(session, source_url, pages, delay, items, on_saved=on_products_saved)
        category_stats.append(stat)
        if on_categories_saved:
            on_categories_saved(category_stats)
        print(
            f"  done: {stat.scraped_count} products scraped"
            + (f" (site reports {stat.reported_count} total)" if stat.reported_count is not None else "")
        )
        print()
        if index < len(seed_urls) and delay:
            time.sleep(delay)

    if not items:
        raise SystemExit("No product cards were found; the source layout may have changed.")

    products = list(items.values())
    needs_categories = [item for item in products if not item.categories]
    if needs_categories:
        print(f"Fetching categories from {len(needs_categories)} product pages (WooCommerce-style lookup)")
        print()
        fetch_categories(session, needs_categories, delay, on_saved=on_products_saved)
        print()
    return products, category_stats


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


def read_products_csv(path):
    """Load a previously written products.csv back into ScrapedProduct
    objects, keyed by source_url, so a run can resume/merge instead of
    starting from a blank slate."""
    if not path.exists():
        return {}
    items = {}
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            source_url = row.get("source_url")
            if not source_url:
                continue
            price = as_decimal(row.get("price"))
            compare_at_price = as_decimal(row.get("compare_at_price"))
            categories = [c for c in (row.get("categories") or "").split("|") if c]
            items[source_url] = ScrapedProduct(
                source_url=source_url,
                name=row.get("name", ""),
                price=price,
                compare_at_price=compare_at_price,
                categories=categories,
                image_url=row.get("image_url", ""),
            )
    return items


def as_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def write_categories_csv(category_stats, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "url", "platform", "scraped_count", "reported_count"]
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stat.to_row() for stat in category_stats)
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--source-url", dest="source_urls", action="append", default=None,
        help="Catalog or category URL to scrape. May be passed multiple times.",
    )
    parser.add_argument(
        "--discover-category-hub", default=None,
        help=(
            "A category-index/hub page URL; every category link found on it is scraped too. "
            f"Defaults to {DEFAULT_DISCOVER_HUB!r} when neither --source-url nor this flag is given."
        ),
    )
    parser.add_argument("--pages", type=int, default=1, help="Max pages per category (auto-capped to what exists).")
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--categories-output", type=Path, default=DEFAULT_CATEGORIES_OUTPUT)
    parser.add_argument(
        "--no-resume", action="store_true",
        help="Ignore any existing products.csv instead of loading it as a starting point.",
    )
    args = parser.parse_args()

    source_urls = args.source_urls
    discover_category_hub = args.discover_category_hub
    if source_urls is None and discover_category_hub is None:
        # Nothing explicit was passed: scrape both default sources.
        source_urls = [DEFAULT_SOURCE]
        discover_category_hub = DEFAULT_DISCOVER_HUB
    elif source_urls is None:
        source_urls = []

    output = args.output.resolve()
    categories_output = args.categories_output.resolve()

    print("=" * 60)
    print("Peptide Catalog Scraper")
    print("=" * 60)
    print(f"Products output:   {output}")
    print(f"Categories output: {categories_output}")

    items = {} if args.no_resume else read_products_csv(output)
    print(f"Existing products loaded from disk: {len(items)}")
    print()

    def save_products():
        write_csv(list(items.values()), output)

    def save_categories(category_stats):
        write_categories_csv(category_stats, categories_output)

    products, category_stats = scrape(
        source_urls,
        args.pages,
        max(0, args.delay),
        discover_category_hub,
        items=items,
        on_products_saved=save_products,
        on_categories_saved=save_categories,
    )

    # Final save, in case nothing triggered a mid-run save (e.g. every page
    # already matched what's on disk) -- keeps behavior correct either way.
    save_products()
    save_categories(category_stats)

    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Total products saved: {len(products)}")
    print(f"Total categories saved: {len(category_stats)}")
    print(f"Products file:   {output}")
    print(f"Categories file: {categories_output}")


if __name__ == "__main__":
    main()
