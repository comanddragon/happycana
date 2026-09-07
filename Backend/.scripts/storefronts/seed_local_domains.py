#!/usr/bin/env python3
"""Configure isolated *.localhost hostnames for the local storefronts."""

import os
import sys
from pathlib import Path

import django
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import transaction

from apps.storefronts.models import (
    Storefront,
    StorefrontDomain,
    StorefrontOrigin,
)

LOCAL_HOSTS = {
    "dispensary": "dispensary.localhost",
    "peptides": "peptides.localhost",
    "hash": "hash.localhost",
}
LEGACY_DOMAINS = {"localhost", "localhost:3000", "127.0.0.1", "127.0.0.1:3000"}
LEGACY_ORIGINS = {"http://localhost:3000", "http://127.0.0.1:3000"}


@transaction.atomic
def main():
    for slug, hostname in LOCAL_HOSTS.items():
        storefront = Storefront.objects.get(slug=slug)
        frontend_url = f"http://{hostname}:3000"
        storefront.frontend_url = frontend_url
        storefront.save(update_fields=["frontend_url", "updated_at"])
        StorefrontDomain.objects.update_or_create(
            domain=hostname,
            defaults={"storefront": storefront, "is_primary": True},
        )
        StorefrontOrigin.objects.update_or_create(
            origin=frontend_url,
            defaults={"storefront": storefront},
        )
        storefront.domains.filter(domain__in=LEGACY_DOMAINS).delete()
        storefront.origins.filter(origin__in=LEGACY_ORIGINS).delete()
        print(f"{slug}: {frontend_url}")


if __name__ == "__main__":
    main()
