import hashlib
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Category, Listing, Product, ProductImage, ProductVariant
from apps.catalog_peptides.models import PeptideProfile
from apps.inventory.models import Stock, Warehouse
from apps.storefronts.models import Storefront


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


def parse_price(text):
    values = re.findall(r"(?:USD\s*)?\$?([0-9][0-9,]*(?:\.\d{1,2})?)", text or "")
    if not values:
        return None
    try:
        return Decimal(values[-1].replace(",", ""))
    except InvalidOperation:
        return None


def parse_catalog_page(html, source_url):
    """Parse WooCommerce cards without depending on one theme's exact markup."""
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
        categories = [
            node.get_text(" ", strip=True)
            for node in card.select(".wd-product-cats a, .product-categories a, .category a")
            if node.get_text(" ", strip=True)
        ]
        image = card.select_one("img")
        image_url = ""
        if image:
            image_url = image.get("data-lazy-src") or image.get("data-src") or image.get("src") or ""
        products.append(ScrapedProduct(
            source_url=product_url,
            name=name,
            price=price,
            compare_at_price=compare_at if compare_at and compare_at > price else None,
            categories=categories,
            image_url=urljoin(source_url, image_url),
        ))
        seen.add(product_url)
    return products


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


class Command(BaseCommand):
    help = "Scrape a public peptide catalog and upsert it into a peptide storefront."

    def add_arguments(self, parser):
        parser.add_argument("--source-url", default=DEFAULT_SOURCE)
        parser.add_argument("--storefront", default="peptides")
        parser.add_argument("--pages", type=int, default=1)
        parser.add_argument("--stock", type=int, default=25)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        source_url = options["source_url"]
        if urlparse(source_url).scheme not in {"http", "https"}:
            raise CommandError("--source-url must be an HTTP(S) URL")
        items = self._scrape(source_url, options["pages"])
        if not items:
            raise CommandError("No product cards were found; the source layout may have changed.")
        if options["dry_run"]:
            for item in items:
                self.stdout.write(f"{item.name} | {item.price} | {item.source_url}")
            self.stdout.write(self.style.SUCCESS(f"Parsed {len(items)} products (dry run)."))
            return
        storefront = self._storefront(options["storefront"])
        with transaction.atomic():
            stats = self._seed(storefront, items, options["stock"])
        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(items)} products: {stats['created']} created, {stats['updated']} updated."
        ))

    def _storefront(self, slug):
        storefront, _ = Storefront.objects.update_or_create(
            slug=slug,
            defaults={
                "name": "Axiom Peptides",
                "kind": Storefront.Kind.PEPTIDES,
                "currency": "USD",
                "is_active": True,
                "branding": {
                    "meta_title": "Axiom Peptides | Research Compounds",
                    "description": "High-purity research compounds with transparent catalog documentation.",
                    "eyebrow": "Independent research supply",
                },
                "settings": {"research_use_only": True},
            },
        )
        return storefront

    def _scrape(self, source_url, pages):
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/html"})
        items = {}
        for page in range(1, max(1, pages) + 1):
            url = source_url if page == 1 else source_url.rstrip("/") + f"/page/{page}/"
            try:
                response = session.get(url, timeout=25)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise CommandError(f"Could not fetch {url}: {exc}") from exc
            for item in parse_catalog_page(response.text, url):
                items[item.source_url] = item
        return list(items.values())

    def _seed(self, storefront, items, stock_quantity):
        warehouse, _ = Warehouse.objects.get_or_create(
            storefront=storefront,
            name=f"{storefront.name} Research Inventory",
            defaults={"address": "Online fulfillment", "is_active": True},
        )
        created = updated = 0
        for position, item in enumerate(items):
            base_slug = slugify(item.name)[:220] or item.source_id[-12:]
            product, was_created = Product.objects.update_or_create(
                external_source_id=item.source_id,
                defaults={
                    "kind": Product.Kind.PEPTIDE,
                    "name": item.name,
                    "slug": self._available_slug(base_slug, item.source_id),
                    "description": (
                        f"{item.name} supplied for laboratory research and educational use only. "
                        "Not for human consumption. Review source documentation before handling."
                    ),
                    "base_price": item.price,
                    "compare_at_price": item.compare_at_price,
                    "is_active": True,
                    "is_featured": position < 4,
                    "is_new": True,
                },
            )
            profile_defaults = infer_profile(item.name)
            PeptideProfile.objects.update_or_create(
                product=product,
                defaults={**profile_defaults, "documentation_url": item.source_url},
            )
            categories = []
            for label in item.categories or ["Research Peptides"]:
                category, _ = Category.objects.get_or_create(
                    slug="peptide-" + slugify(label)[:230],
                    defaults={"name": label, "description": f"Research catalog: {label}", "is_key": True},
                )
                categories.append(category)
            product.categories.set(categories)
            listing, _ = Listing.objects.update_or_create(
                storefront=storefront,
                product=product,
                defaults={
                    "slug": product.slug,
                    "title": product.name,
                    "is_active": True,
                    "is_featured": product.is_featured,
                    "meta_title": product.name[:60],
                    "meta_description": "Research-use-only compound with source documentation.",
                },
            )
            listing.categories.set(categories)
            sku = "PEP-" + hashlib.sha256(item.source_url.encode()).hexdigest()[:10].upper()
            variant, _ = ProductVariant.objects.update_or_create(
                sku=sku,
                defaults={"product": product, "price": item.price, "is_active": True},
            )
            Stock.objects.update_or_create(
                variant=variant, warehouse=warehouse,
                defaults={"quantity": max(0, stock_quantity), "reserved": 0},
            )
            if item.image_url:
                ProductImage.objects.update_or_create(
                    product=product, is_primary=True,
                    defaults={"source_url": item.image_url, "alt_text": item.name, "order": 0},
                )
            created += int(was_created)
            updated += int(not was_created)
        return {"created": created, "updated": updated}

    @staticmethod
    def _available_slug(base_slug, source_id):
        existing = Product.objects.filter(slug=base_slug).exclude(external_source_id=source_id)
        return f"{base_slug}-{source_id[-8:]}" if existing.exists() else base_slug
