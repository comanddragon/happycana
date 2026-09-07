import requests
from bs4 import BeautifulSoup

url = "https://www.peptidessource.com/product-category/research-peptides-by-type/regeneration-longevity/"

s = requests.Session()
s.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})

r = s.get(url, timeout=30)

print("status:", r.status_code)
print("final URL:", r.url)
print("content type:", r.headers.get("content-type"))
print("bytes:", len(r.content))

soup = BeautifulSoup(r.text, "html.parser")

print("title:", soup.title.get_text(" ", strip=True) if soup.title else None)
print("product links:", len(soup.select('a[href*="/product/"]')))
print("product cards:", len(soup.select("li.product")))
print("forms:", len(soup.select("form")))

print("\nFirst 500 characters:")
print(r.text[:500])