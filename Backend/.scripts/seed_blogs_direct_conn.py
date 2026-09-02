import argparse
import json
import logging
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
# in BlogPost.save() (apps/blog/models.py).
from apps.blog.utils import clean_content_html, compute_read_time

DEFAULT_PATH = BACKEND_DIR / ".output" / "blogs" / "blogs.json"

logger = logging.getLogger("seed_blogs")

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


def configure_logging(verbose: bool = False) -> None:
    """Configure console logging."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.debug("Verbose logging enabled.")


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
    parser = argparse.ArgumentParser(
        description="Seed blog_posts from blogs.json, raw SQL."
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_PATH),
        help=f"Path to blogs.json (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--dsn",
        default=None,
        help="Postgres DSN. Defaults to the DATABASE_URL env var.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and report without writing to the database.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging.",
    )

    args = parser.parse_args()
    configure_logging(args.verbose)

    logger.info("Starting blog seed.")
    logger.info("Input file: %s", args.file)

    if args.dry_run:
        logger.info("Dry-run mode enabled. No database writes will occur.")

    # ------------------------------------------------------------------
    # Load JSON
    # ------------------------------------------------------------------
    logger.info("Loading blogs JSON...")

    try:
        with open(args.file, encoding="utf-8") as f:
            entries = json.load(f)
    except FileNotFoundError:
        logger.error("No such file: %s", args.file)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", args.file, exc)
        sys.exit(1)

    if not isinstance(entries, list):
        logger.error("Expected blogs.json to contain a JSON array of blog posts.")
        sys.exit(1)

    logger.info("Loaded %d entries from JSON.", len(entries))

    # ------------------------------------------------------------------
    # Prepare rows
    # ------------------------------------------------------------------
    rows = []
    skipped = 0

    logger.info("Preparing database rows...")

    for index, entry in enumerate(entries, start=1):
        title = (entry.get("title") or "").strip()
        url = (entry.get("url") or "").strip()

        logger.debug(
            "Processing entry %d/%d: title=%r url=%r",
            index,
            len(entries),
            title,
            url,
        )

        if not title:
            skipped += 1
            logger.warning(
                "Skipping entry %d/%d because it has no title.",
                index,
                len(entries),
            )
            continue

        slug = _slug_from_url(url, title)
        content_text = (entry.get("content_text") or "").strip()
        read_time = compute_read_time(content_text)

        row = {
            "id": str(uuid.uuid4()),
            "slug": slug,
            "title": title,
            "description": (entry.get("description") or "").strip(),
            "content_html": _clean_html(entry.get("content_html")),
            "content_text": content_text,
            "author": (entry.get("author") or "").strip(),
            "image": (entry.get("image") or "").strip(),
            "tags": psycopg2.extras.Json(entry.get("tags") or []),
            "source_url": url,
            "published_at": (entry.get("published_at") or None),
            "is_published": True,
            "read_time": read_time,
        }

        rows.append(row)

        logger.debug(
            "Prepared row: slug=%r read_time=%s author=%r tags=%s",
            slug,
            read_time,
            row["author"],
            entry.get("tags") or [],
        )

    logger.info(
        "Prepared %d rows; %d entries skipped.",
        len(rows),
        skipped,
    )

    # ------------------------------------------------------------------
    # Dry run
    # ------------------------------------------------------------------
    if args.dry_run:
        logger.info("Dry-run results:")

        for row in rows:
            logger.info(
                "[dry-run] slug=%s | title=%s | read_time=%s",
                row["slug"],
                row["title"],
                row["read_time"],
            )

        logger.info(
            "Dry run complete. %d prepared, %d skipped, %d total. Nothing written.",
            len(rows),
            skipped,
            len(entries),
        )
        return

    # ------------------------------------------------------------------
    # Database configuration
    # ------------------------------------------------------------------
    logger.info("Loading environment variables...")

    load_dotenv()

    dsn = args.dsn or os.environ.get("DATABASE_URL")

    if not dsn:
        logger.error("No DSN given and DATABASE_URL is not set.")
        sys.exit(1)

    # Avoid logging the full DSN because it may contain credentials.
    logger.info(
        "Database connection configured from %s.",
        "--dsn" if args.dsn else "DATABASE_URL",
    )

    # ------------------------------------------------------------------
    # Database connection
    # ------------------------------------------------------------------
    logger.info("Connecting to PostgreSQL...")

    try:
        conn = psycopg2.connect(dsn)
    except psycopg2.Error:
        logger.exception("Failed to connect to PostgreSQL.")
        sys.exit(1)

    logger.info("Connected to PostgreSQL.")

    created = 0
    updated = 0

    try:
        with conn:
            logger.info("Beginning database transaction.")

            with conn.cursor() as cur:
                for index, row in enumerate(rows, start=1):
                    logger.debug(
                        "Upserting %d/%d: slug=%s title=%r",
                        index,
                        len(rows),
                        row["slug"],
                        row["title"],
                    )

                    try:
                        cur.execute(UPSERT_SQL, row)
                        (inserted,) = cur.fetchone()

                    except psycopg2.Error:
                        logger.exception(
                            "Database error while upserting slug=%s",
                            row["slug"],
                        )
                        raise

                    if inserted:
                        created += 1
                        logger.info(
                            "[CREATED] %s — %s",
                            row["slug"],
                            row["title"],
                        )
                    else:
                        updated += 1
                        logger.info(
                            "[UPDATED] %s — %s",
                            row["slug"],
                            row["title"],
                        )

            logger.info("Transaction completed successfully.")

    except Exception:
        logger.exception(
            "Seed failed. Transaction will be rolled back."
        )
        raise

    finally:
        conn.close()
        logger.info("Database connection closed.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    logger.info(
        "Done. %d created, %d updated, %d skipped.",
        created,
        updated,
        skipped,
    )


if __name__ == "__main__":
    main()