import json
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://9realms.eu"
BLOG_URL = f"{BASE_URL}/blogs/news"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
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
DELAY = 0.5

session = requests.Session()
session.headers.update(HEADERS)


def fetch_html(url):
    """Download a page and return its HTML."""
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def clean_text(element):
    """Convert an HTML element to clean text."""
    if not element:
        return ""

    return " ".join(element.get_text(" ", strip=True).split())


def get_article_urls(page_url):
    """
    Extract article URLs from a Shopify blog listing page.
    Returns a set so it can be compared with all_urls.
    """
    html = fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")

    urls = set()

    # Shopify blog article links normally contain /blogs/news/
    for link in soup.select('a[href*="/blogs/news/"]'):
        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(BASE_URL, href)

        # Remove query strings/fragments
        absolute_url = absolute_url.split("?")[0].split("#")[0]

        # Only accept actual article URLs
        if "/blogs/news/" not in absolute_url:
            continue

        # Exclude the blog index
        if absolute_url.rstrip("/") == BLOG_URL.rstrip("/"):
            continue

        urls.add(absolute_url)

    return urls


def get_next_page(page_url):
    """
    Find the next pagination URL.
    """
    html = fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")

    # Common Shopify pagination selectors
    selectors = [
        'a[rel="next"]',
        'a.pagination__next',
        'a[aria-label*="Next"]',
        'a[href*="page="]',
    ]

    for selector in selectors:
        link = soup.select_one(selector)

        if link and link.get("href"):
            href = link["href"]

            # Only accept an actual pagination URL
            if "page=" in href:
                return urljoin(BASE_URL, href)

    return None


def extract_article(url):
    """
    Extract the article information from an individual blog page.
    """
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------
    title = ""

    selectors = [
        "h1.article__title",
        "h1.blog-post__title",
        "article h1",
        "main h1",
        "h1",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            title = clean_text(element)
            break

    # Fallback to <title>
    if not title and soup.title:
        title = clean_text(soup.title)

    # ---------------------------------------------------------
    # Article container
    # ---------------------------------------------------------
    article = None

    selectors = [
        "article",
        ".article__content",
        ".blog-post__content",
        ".article-content",
        ".rte",
        ".rich-text",
        "main",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            article = element
            break

    # ---------------------------------------------------------
    # Content HTML
    # ---------------------------------------------------------
    content_html = ""

    if article:
        # Prefer a specific content container if one exists
        content_candidates = [
            ".article__content",
            ".blog-post__content",
            ".article-content",
            ".rte",
            ".rich-text",
        ]

        content_element = None

        for selector in content_candidates:
            content_element = article.select_one(selector)

            if content_element:
                break

        if content_element:
            content_html = str(content_element)
        else:
            content_html = str(article)

    # ---------------------------------------------------------
    # Content text
    # ---------------------------------------------------------
    content_text = ""

    if article:
        content_text = clean_text(article)

    # ---------------------------------------------------------
    # Publication date
    # ---------------------------------------------------------
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

        if element:
            published_at = (
                element.get("datetime")
                or element.get_text(" ", strip=True)
            )
            break

    # ---------------------------------------------------------
    # Author
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Description / excerpt
    # ---------------------------------------------------------
    description = ""

    meta_description = soup.select_one(
        'meta[name="description"]'
    )

    if meta_description:
        description = meta_description.get("content", "").strip()

    # ---------------------------------------------------------
    # Featured image
    # ---------------------------------------------------------
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
            image = element.get("content", "")
        else:
            image = (
                element.get("src")
                or element.get("data-src")
                or element.get("data-lazy-src")
                or ""
            )

        if image:
            image = urljoin(BASE_URL, image)
            break

    # ---------------------------------------------------------
    # Tags
    # ---------------------------------------------------------
    tags = []

    tag_selectors = [
        'a[href*="/blogs/news/tagged/"]',
        ".article__tags a",
        ".blog-post__tags a",
        ".tags a",
    ]

    for selector in tag_selectors:
        for element in soup.select(selector):
            tag = clean_text(element)

            if tag and tag not in tags:
                tags.append(tag)

    return {
        "title": title,
        "url": url,
        "published_at": published_at,
        "author": author,
        "description": description,
        "image": image,
        "tags": tags,
        "content_html": content_html,
        "content_text": content_text,
    }


def discover_all_article_urls():
    """
    Crawl the Shopify blog index and collect article URLs.
    """
    all_urls = set()
    page = 1

    while True:
        page_url = BLOG_URL

        if page > 1:
            page_url = f"{BLOG_URL}?page={page}"

        print(f"Discovering blog page {page}: {page_url}")

        try:
            urls = get_article_urls(page_url)
        except requests.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")
            break

        if not urls:
            print("No articles found on this page.")
            break

        new_urls = urls - all_urls

        if not new_urls:
            print("No new articles found. Stopping.")
            break

        all_urls.update(new_urls)

        print(
            f"Found {len(new_urls)} new articles "
            f"(total: {len(all_urls)})"
        )

        page += 1
        time.sleep(DELAY)

    return sorted(all_urls)


def main():
    print("=" * 60)
    print("9Realms Blog Scraper")
    print("=" * 60)

    # ---------------------------------------------------------
    # Step 1: Discover article URLs
    # ---------------------------------------------------------
    article_urls = discover_all_article_urls()

    print()
    print(f"Total articles discovered: {len(article_urls)}")
    print()

    # ---------------------------------------------------------
    # Step 2: Scrape individual articles
    # ---------------------------------------------------------
    articles = []

    for index, url in enumerate(article_urls, start=1):
        print(
            f"[{index}/{len(article_urls)}] "
            f"Fetching {url}"
        )

        try:
            article = extract_article(url)
            articles.append(article)

            print(f"  Title: {article['title']}")

        except requests.RequestException as e:
            print(f"  Request failed: {e}")

        except Exception as e:
            print(f"  Parsing failed: {e}")

        time.sleep(DELAY)

    # ---------------------------------------------------------
    # Step 3: Save JSON
    # ---------------------------------------------------------
    with open(
        "blogs.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 60)
    print(f"Saved {len(articles)} articles to blogs.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
