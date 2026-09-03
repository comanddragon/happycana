import csv
import random
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://9realms.eu"
BLOG_URL = f"{BASE_URL}/blogs/news"

# Save here:
OUTPUT_DIR = Path(__file__).resolve().parents[2] / ".output" / "blogs"
OUTPUT_FILE = OUTPUT_DIR / "blogs.csv"
FIELDS = [
    "title", "url", "source_url", "published_at", "author", "description",
    "image", "tags", "content_html", "content_text",
]
LEGACY_HOSTS = {"9realms.eu", "www.9realms.eu", "9realms.de", "www.9realms.de"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 30
DELAY = 1.0
MAX_RETRIES = 7
BACKOFF_SECONDS = 2.0


# ============================================================
# SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# HTTP
# ============================================================

def fetch_html(url):
    """
    Download a page and return its HTML.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=TIMEOUT)
            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
                return response.text
            if attempt == MAX_RETRIES:
                response.raise_for_status()

            try:
                wait = float(response.headers.get("Retry-After", ""))
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


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(element):
    """
    Convert an HTML element into clean text.
    """
    if not element:
        return ""

    return " ".join(
        element.get_text(" ", strip=True).split()
    )


def resolve_internal_url(value):
    if not isinstance(value, str) or not value.strip():
        return value
    value = value.strip()
    if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return value
    parsed = urlsplit(value)
    if parsed.netloc and parsed.netloc.lower() not in LEGACY_HOSTS:
        return value
    parts = [part for part in parsed.path.split("/") if part]
    path, query = None, parsed.query
    if len(parts) >= 3 and parts[:2] == ["blogs", "news"]:
        path = f"/blog/{parts[2]}"
    elif parts == ["blogs", "news"]:
        path = "/blog"
    elif len(parts) >= 2 and parts[0] == "products":
        path = f"/shop/products/{parts[1]}"
    elif parts == ["collections"]:
        path = "/shop"
    elif len(parts) >= 2 and parts[0] == "collections":
        path = "/shop/products"
        params = dict(parse_qsl(query, keep_blank_values=True))
        params["category"] = parts[1]
        query = urlencode(params)
    return urlunsplit(("", "", path, query, parsed.fragment)) if path else value


def clean_content_html(html):
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup.find_all(["script", "style", "link"]):
        tag.decompose()
    for tag in soup.find_all(True):
        for attribute in ("href", "src", "data-src", "poster", "action"):
            if isinstance(tag.get(attribute), str):
                tag[attribute] = resolve_internal_url(tag[attribute])
        for attribute in ("srcset", "data-srcset"):
            if not isinstance(tag.get(attribute), str):
                continue
            candidates = []
            for candidate in tag[attribute].split(","):
                bits = candidate.strip().split()
                if bits:
                    bits[0] = resolve_internal_url(bits[0])
                candidates.append(" ".join(bits))
            tag[attribute] = ", ".join(candidates)
        if tag.name == "img":
            if not tag.get("src") and tag.get("data-src"):
                tag["src"] = tag["data-src"]
            if not tag.get("srcset") and tag.get("data-srcset"):
                tag["srcset"] = tag["data-srcset"]
    # Keep each CSV record on one physical line so it remains usable in editors.
    return str(soup).replace("\r", " ").replace("\n", " ")


# ============================================================
# ARTICLE URL DISCOVERY
# ============================================================

def get_article_urls(page_url):
    """
    Extract article URLs from a Shopify blog listing page.

    Returns a SET so URLs can easily be compared with
    already-discovered URLs.
    """

    html = fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")

    urls = set()

    for link in soup.select('a[href*="/blogs/news/"]'):

        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            BASE_URL,
            href,
        )

        # Remove query strings and fragments
        absolute_url = (
            absolute_url
            .split("?")[0]
            .split("#")[0]
            .rstrip("/")
        )

        # Must be a /blogs/news/ URL
        if "/blogs/news/" not in absolute_url:
            continue

        # Exclude blog homepage
        if absolute_url == BLOG_URL.rstrip("/"):
            continue

        urls.add(absolute_url)

    return urls


# ============================================================
# ARTICLE EXTRACTION
# ============================================================

def extract_article(url):
    """
    Extract information from an individual blog article.
    """

    html = fetch_html(url)
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = ""

    title_selectors = [
        "h1.article__title",
        "h1.blog-post__title",
        "article h1",
        "main h1",
        "h1",
    ]

    for selector in title_selectors:

        element = soup.select_one(selector)

        if element:
            title = clean_text(element)
            break

    # Fallback
    if not title and soup.title:
        title = clean_text(soup.title)

    # --------------------------------------------------------
    # ARTICLE CONTENT
    # --------------------------------------------------------

    article = None

    article_selectors = [
        ".article__content",
        ".blog-post__content",
        ".article-content",
        "article",
        ".rte",
        ".rich-text",
        "main",
    ]

    for selector in article_selectors:

        element = soup.select_one(selector)

        if element:
            article = element
            break

    # --------------------------------------------------------
    # CONTENT HTML
    # --------------------------------------------------------

    content_html = ""

    if article:

        content_element = None

        content_selectors = [
            ".article__content",
            ".blog-post__content",
            ".article-content",
            ".rte",
            ".rich-text",
        ]

        for selector in content_selectors:

            element = article.select_one(selector)

            if element:
                content_element = element
                break

        if content_element:
            content_html = str(
                content_element
            )
        else:
            content_html = str(article)

    # --------------------------------------------------------
    # CONTENT TEXT
    # --------------------------------------------------------

    content_text = ""

    if article:
        content_text = clean_text(article)

    # --------------------------------------------------------
    # PUBLICATION DATE
    # --------------------------------------------------------

    published_at = ""

    date_selectors = [
        "time[datetime]",
        "time",
        ".article__date",
        ".blog-post__date",
        ".article-date",
        ".published",
    ]

    for selector in date_selectors:

        element = soup.select_one(selector)

        if not element:
            continue

        published_at = (
            element.get("datetime")
            or element.get_text(
                " ",
                strip=True,
            )
        )

        if published_at:
            break

    # --------------------------------------------------------
    # AUTHOR
    # --------------------------------------------------------

    author = ""

    author_selectors = [
        '[rel="author"]',
        ".article__author",
        ".blog-post__author",
        ".author",
    ]

    for selector in author_selectors:

        element = soup.select_one(selector)

        if element:
            author = clean_text(element)
            break

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = ""

    meta_description = soup.select_one(
        'meta[name="description"]'
    )

    if meta_description:
        description = (
            meta_description
            .get("content", "")
            .strip()
        )

    # --------------------------------------------------------
    # FEATURED IMAGE
    # --------------------------------------------------------

    image = ""

    image_selectors = [
        'meta[property="og:image"]',
        'meta[name="twitter:image"]',
        "article img",
        "main img",
    ]

    for selector in image_selectors:

        element = soup.select_one(selector)

        if not element:
            continue

        if element.name == "meta":

            image = element.get(
                "content",
                "",
            )

        else:

            image = (
                element.get("src")
                or element.get("data-src")
                or element.get("data-lazy-src")
                or ""
            )

        if image:
            image = urljoin(
                BASE_URL,
                image,
            )
            break

    # --------------------------------------------------------
    # TAGS
    # --------------------------------------------------------

    tags = []

    tag_selectors = [
        'a[href*="/blogs/news/tagged/"]',
        ".article__tags a",
        ".blog-post__tags a",
        ".tags a",
    ]

    for selector in tag_selectors:

        for element in soup.select(
            selector
        ):

            tag = clean_text(element)

            if tag and tag not in tags:
                tags.append(tag)

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "title": title,
        "url": resolve_internal_url(url),
        "source_url": url,
        "published_at": published_at,
        "author": author,
        "description": description,
        "image": image,
        "tags": "|".join(tags),
        "content_html": clean_content_html(content_html),
        "content_text": content_text,
    }


# ============================================================
# LOAD EXISTING DATA
# ============================================================

def load_existing_articles():
    """
    Load blogs.csv if it already exists.

    This allows the scraper to resume after interruption.
    """

    if not OUTPUT_FILE.exists():
        return []

    try:

        with OUTPUT_FILE.open(encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))
    except (csv.Error, UnicodeDecodeError) as exc:
        print(f"Warning: cannot read {OUTPUT_FILE}: {exc}")
        return []


# ============================================================
# SAVE DATA
# ============================================================

def save_articles(articles):
    """
    Save articles to disk.

    This is called after EVERY article so data is not lost
    if the scraper crashes.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write to a temporary file first.
    # This prevents a crash during writing from corrupting the main CSV file.
    temp_file = OUTPUT_FILE.with_suffix(".csv.tmp")

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(articles)

    # Replace the old file atomically
    temp_file.replace(
        OUTPUT_FILE
    )


# ============================================================
# DISCOVER ALL ARTICLE URLS
# ============================================================

def discover_all_article_urls():
    """
    Crawl Shopify blog pagination and collect article URLs.
    """

    all_urls = set()

    page = 1

    while True:

        page_url = BLOG_URL

        if page > 1:
            page_url = (
                f"{BLOG_URL}?page={page}"
            )

        print(
            f"Discovering blog page {page}: "
            f"{page_url}"
        )

        try:

            urls = get_article_urls(
                page_url
            )

        except requests.RequestException as e:

            print(
                f"Failed to fetch page {page}: {e}"
            )

            break

        if not urls:

            print(
                "No articles found on this page."
            )

            break

        new_urls = urls - all_urls

        if not new_urls:

            print(
                "No new articles found. "
                "Stopping pagination."
            )

            break

        all_urls.update(
            new_urls
        )

        print(
            f"Found {len(new_urls)} new articles "
            f"(total: {len(all_urls)})"
        )

        page += 1

        time.sleep(DELAY)

    return sorted(all_urls)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("9Realms Blog Scraper")
    print("=" * 60)

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # LOAD EXISTING ARTICLES
    # --------------------------------------------------------

    articles = load_existing_articles()

    existing_urls = {
        article.get("source_url")
        for article in articles
        if article.get("url")
    }

    print(
        f"Existing articles on disk: "
        f"{len(existing_urls)}"
    )

    # --------------------------------------------------------
    # DISCOVER ARTICLES
    # --------------------------------------------------------

    print()
    print("Discovering article URLs...")
    print()

    article_urls = (
        discover_all_article_urls()
    )

    print()
    print(
        f"Total article URLs discovered: "
        f"{len(article_urls)}"
    )

    # --------------------------------------------------------
    # REMOVE ALREADY SCRAPED ARTICLES
    # --------------------------------------------------------

    urls_to_scrape = [
        url
        for url in article_urls
        if url not in existing_urls
    ]

    print(
        f"Already scraped: "
        f"{len(article_urls) - len(urls_to_scrape)}"
    )

    print(
        f"Remaining to scrape: "
        f"{len(urls_to_scrape)}"
    )

    print()

    # --------------------------------------------------------
    # SCRAPE ARTICLES
    # --------------------------------------------------------

    for index, url in enumerate(
        urls_to_scrape,
        start=1,
    ):

        print(
            f"[{index}/{len(urls_to_scrape)}] "
            f"Fetching:"
        )

        print(
            f"  {url}"
        )

        try:

            article = extract_article(
                url
            )

            # Make sure we actually extracted something
            if not article["title"]:

                print(
                    "  WARNING: No title found."
                )

            if not article["content_text"]:

                print(
                    "  WARNING: No article content found."
                )

            # Add article to memory
            articles.append(
                article
            )

            # ------------------------------------------------
            # SAVE IMMEDIATELY
            # ------------------------------------------------

            save_articles(
                articles
            )

            print(
                f"  Saved: {article['title']}"
            )

            print(
                f"  Total saved: "
                f"{len(articles)}"
            )

        except requests.RequestException as e:

            print(
                f"  REQUEST ERROR: {e}"
            )

        except Exception as e:

            print(
                f"  ERROR: {type(e).__name__}: {e}"
            )

        # Don't hammer the website
        time.sleep(DELAY)

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)

    print(
        f"Total articles saved: "
        f"{len(articles)}"
    )

    print(
        f"File: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
