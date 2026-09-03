"""
Seed BlogPost rows into the database from scrape_blogs.py's cleaned CSV.

Usage:
    python Backend/.scripts/blogs/seed_blogs.py [--file PATH] [--dry-run]

Relies on the same environment as manage.py — DJANGO_SETTINGS_MODULE (and
DATABASE_URL, for production settings) must already be set, e.g. via a
loaded .env file, so this writes to whichever database that env points at
(Neon in production).
"""
import argparse
import csv
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import django
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings  # noqa: E402
from django.utils.dateparse import parse_datetime  # noqa: E402
from django.utils import timezone  # noqa: E402
from slugify import slugify  # noqa: E402

from apps.blog.models import BlogPost  # noqa: E402

DEFAULT_PATH = BACKEND_DIR / ".output" / "blogs" / "blogs.csv"
LOCAL_DATABASE_HOSTS = {"", "localhost", "127.0.0.1", "::1"}

# Strips <script>/<style> blocks out of scraped HTML before it's stored —
# the source pages ship carousel/tracking scripts that have no business
# running on our own domain. Images, links, tables, etc. are left as-is.
_STRIP_TAGS_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)


def _slug_from_url(url: str, title: str) -> str:
    if url:
        path = urlparse(url).path.rstrip("/")
        last_segment = path.rsplit("/", 1)[-1]
        if last_segment:
            return slugify(last_segment)
    return slugify(title)


def _parse_published_at(value):
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    return dt


def _clean_html(html: str) -> str:
    return _STRIP_TAGS_RE.sub("", html or "")


def verify_database_target(allow_remote: bool) -> None:
    database = settings.DATABASES["default"]
    host = str(database.get("HOST") or "")
    name = str(database.get("NAME") or "")
    settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    print(f"Settings: {settings_module}")
    print(f"Database: {name} on {host or 'local socket'}")
    if host not in LOCAL_DATABASE_HOSTS and not host.startswith("/") and not allow_remote:
        sys.exit(
            f"Refusing to seed remote database host {host!r}. "
            "Use local DB_* values or pass --allow-remote-db intentionally."
        )


def main():
    parser = argparse.ArgumentParser(description="Seed BlogPost rows from the cleaned blogs CSV.")
    parser.add_argument("--file", default=str(DEFAULT_PATH), help=f"Path to blogs.csv (default: {DEFAULT_PATH})")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing to the database.")
    parser.add_argument("--allow-remote-db", action="store_true", help="Explicitly permit seeding a non-local database.")
    args = parser.parse_args()

    verify_database_target(args.allow_remote_db)

    try:
        with open(args.file, encoding="utf-8", newline="") as f:
            entries = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.exit(f"No such file: {args.file}")
    except (csv.Error, UnicodeDecodeError) as exc:
        sys.exit(f"Invalid CSV in {args.file}: {exc}")

    created, updated, skipped = 0, 0, 0

    for entry in entries:
        title = (entry.get("title") or "").strip()
        url = (entry.get("url") or "").strip()
        source_url = (entry.get("source_url") or url).strip()

        if not title:
            skipped += 1
            print("Skipping entry with no title.", file=sys.stderr)
            continue

        slug = _slug_from_url(url, title)

        defaults = {
            "title": title,
            "description": (entry.get("description") or "").strip(),
            "content_html": _clean_html(entry.get("content_html")),
            "content_text": (entry.get("content_text") or "").strip(),
            "author": (entry.get("author") or "").strip(),
            "image": (entry.get("image") or "").strip(),
            "tags": [tag for tag in (entry.get("tags") or "").split("|") if tag],
            "source_url": source_url,
            "published_at": _parse_published_at(entry.get("published_at")),
        }

        if args.dry_run:
            print(f"[dry-run] {slug}: {title}")
            continue

        obj, was_created = BlogPost.objects.update_or_create(slug=slug, defaults=defaults)
        created += was_created
        updated += not was_created

    if args.dry_run:
        print(f"{len(entries)} entries parsed (dry run, nothing written).")
        return

    print(f"Done. {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
