#!/usr/bin/env python3
"""Seed missing category covers from real product photography.

The product scrapers retain their source image URLs, while Category.image is
an uploaded ImageField. This script bridges the two without inventing artwork:
for every storefront category without an upload, it downloads the first usable
image belonging to an active listing in that category and stores the optimized
AVIF through Category.save(). Existing category uploads are never overwritten.

Examples:
    python .scripts/storefronts/seed_category_images.py --storefront peptides
    python .scripts/storefronts/seed_category_images.py --storefront hash
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import django
import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[1]
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}

load_dotenv(BACKEND_DIR / ".env")
load_dotenv()
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile

from apps.catalog.models import Category, ProductImage
from apps.storefronts.models import Storefront


def verify_database_target(allow_remote):
    database = settings.DATABASES["default"]
    host = str(database.get("HOST") or "")
    name = str(database.get("NAME") or "")
    print(f"Settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    print(f"Database: {name} on {host or 'local socket'}")
    if host not in LOCAL_DATABASE_HOSTS and not host.startswith("/") and not allow_remote:
        raise SystemExit(
            f"Refusing to seed remote database host {host!r}. "
            "Use local DB_* values or pass --allow-remote-db intentionally."
        )


def extension_for(response, url):
    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
    by_type = {
        "image/avif": ".avif",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    if content_type in by_type:
        return by_type[content_type]
    suffix = Path(urlsplit(url).path).suffix.lower()
    return suffix if suffix in {".avif", ".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


def candidate_images(category, storefront):
    return (
        ProductImage.objects.filter(
            product__categories=category,
            product__listings__storefront=storefront,
            product__listings__is_active=True,
            product__is_active=True,
        )
        .exclude(source_url="")
        .order_by("-is_primary", "order", "product__name", "id")
        .values_list("source_url", flat=True)
        .distinct()
    )


def seed_category(category, storefront):
    if category.image:
        return "existing"

    for url in candidate_images(category, storefront):
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            if not response.headers.get("content-type", "").lower().startswith("image/"):
                continue
            digest = hashlib.sha256(url.encode()).hexdigest()[:12]
            filename = f"{category.slug}-{digest}{extension_for(response, url)}"
            category.image.save(filename, ContentFile(response.content), save=True)
            print(f"Seeded {category.slug} <- {url}")
            return "seeded"
        except (requests.RequestException, OSError, ValueError) as error:
            print(f"Skipped candidate for {category.slug}: {error}")
    print(f"No usable product image for {category.slug}")
    return "missing"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storefront", required=True)
    parser.add_argument("--allow-remote-db", action="store_true")
    args = parser.parse_args()

    verify_database_target(args.allow_remote_db)
    storefront = Storefront.objects.get(slug=args.storefront, is_active=True)
    categories = (
        Category.objects.filter(
            listings__storefront=storefront,
            listings__is_active=True,
            is_active=True,
        )
        .distinct()
        .order_by("name")
    )
    counts = {"seeded": 0, "existing": 0, "missing": 0}
    for category in categories:
        counts[seed_category(category, storefront)] += 1
    print(
        f"Done: {counts['seeded']} seeded, {counts['existing']} already present, "
        f"{counts['missing']} missing."
    )


if __name__ == "__main__":
    main()
