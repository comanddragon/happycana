"""
Seed blog_posts rows into Postgres from a scraped blogs.json export —
straight psycopg2, no Django ORM/settings involved.

Usage:
    python Backend/.scripts/seed_blogs.py [--file PATH] [--dsn DSN] [--dry-run]

Connects with --dsn if given, otherwise the DATABASE_URL env var (loaded
from .env if present). Whatever that resolves to is what gets written to —
point it at Neon's connection string to seed Neon directly.

Assumes the blog_posts table already exists (run the Django migration
for apps.blog once, the usual way, before running this).
"""
import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from slugify import slugify

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Reuses the exact same HTML-cleaning/read-time logic the Django app uses
# in BlogPost.save() (apps/blog/models.py) — apps/blog/utils.py has no
# Django-settings dependency, so it's safe to import here even though this
# script deliberately avoids booting Django/the ORM otherwise. Keeps rows
# written by this script consistent with rows written through the admin/
# ORM, instead of drifting apart (this script previously had its own,
# thinner <script>/<style>-only strip regex).
from apps.blog.utils import clean_content_html, compute_read_time

DEFAULT_PATH = BACKEND_DIR / ".output" / "blogs" / "blogs.json"

UPSERT_SQL = """
    INSERT INTO blog_posts (
        id, slug, title, description, content_html, content_text,
        author, image, tags, source_url, published_at, is_published,
        read_time, created_at, updated_at
    )
    VALUES (
        %(id)s, %(slug)s, %(title)s, %(description)s, %(content_html)s, %(content_text)s,
        %(author)s, %(image)s, %(tags)s, %(source_url)s, %(published_at)s, %(is_published)s,
        %(read_time)s, now(), now()
    )
    ON CONFLICT (slug) DO UPDATE SET
        title         = EXCLUDED.title,
        description   = EXCLUDED.description,
        content_html  = EXCLUDED.content_html,
        content_text  = EXCLUDED.content_text,
        author        = EXCLUDED.author,
        image         = EXCLUDED.image,
        tags          = EXCLUDED.tags,
        source_url    = EXCLUDED.source_url,
        published_at  = EXCLUDED.published_at,
        read_time     = EXCLUDED.read_time,
        updated_at    = now()
    RETURNING (xmax = 0) AS inserted
"""


def _slug_from_url(url: str, title: str) -> str:
    if url:
        path = urlparse(url).path.rstrip("/")
        last_segment = path.rsplit("/", 1)[-1]
        if last_segment:
            return slugify(last_segment)
    return slugify(title)


def _clean_html(html: str) -> str:
    return clean_content_html(html or "")


def main():
    parser = argparse.ArgumentParser(description="Seed blog_posts from blogs.json, raw SQL.")
    parser.add_argument("--file", default=str(DEFAULT_PATH), help=f"Path to blogs.json (default: {DEFAULT_PATH})")
    parser.add_argument("--dsn", default=None, help="Postgres DSN. Defaults to the DATABASE_URL env var.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing to the database.")
    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            entries = json.load(f)
    except FileNotFoundError:
        sys.exit(f"No such file: {args.file}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Invalid JSON in {args.file}: {exc}")

    if not isinstance(entries, list):
        sys.exit("Expected blogs.json to contain a JSON array of blog posts.")

    rows = []
    skipped = 0
    for entry in entries:
        title = (entry.get("title") or "").strip()
        url = (entry.get("url") or "").strip()

        if not title:
            skipped += 1
            print("Skipping entry with no title.", file=sys.stderr)
            continue

        rows.append({
            "id": str(uuid.uuid4()),
            "slug": _slug_from_url(url, title),
            "title": title,
            "description": (entry.get("description") or "").strip(),
            "content_html": _clean_html(entry.get("content_html")),
            "content_text": (entry.get("content_text") or "").strip(),
            "author": (entry.get("author") or "").strip(),
            "image": (entry.get("image") or "").strip(),
            "tags": psycopg2.extras.Json(entry.get("tags") or []),
            "source_url": url,
            "published_at": (entry.get("published_at") or None),
            "is_published": True,
            "read_time": compute_read_time(entry.get("content_text") or ""),
        })

    if args.dry_run:
        for row in rows:
            print(f"[dry-run] {row['slug']}: {row['title']}")
        print(f"{len(entries)} entries parsed (dry run, nothing written).")
        return

    load_dotenv()
    dsn = args.dsn or os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("No DSN given and DATABASE_URL is not set.")

    created, updated = 0, 0
    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(UPSERT_SQL, row)
                    (inserted,) = cur.fetchone()
                    created += inserted
                    updated += not inserted
    finally:
        conn.close()

    print(f"Done. {created} created, {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()