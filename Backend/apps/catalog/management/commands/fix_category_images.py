import mimetypes

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Category


class Command(BaseCommand):
    help = (
        "Fix Category.image fields that were set to a raw external URL string "
        "(e.g. from a CSV import) instead of an actual uploaded file. "
        "Downloads the image from the stored URL and re-saves it properly."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List affected categories without downloading or saving anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        broken = [c for c in Category.objects.all() if c.image and c.image.name.startswith("http")]

        if not broken:
            self.stdout.write(self.style.SUCCESS("No broken category images found."))
            return

        for category in broken:
            url = category.image.name
            self.stdout.write(f"{category.slug}: {url}")

            if dry_run:
                continue

            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as exc:
                self.stderr.write(self.style.ERROR(f"  failed to fetch: {exc}"))
                continue

            ext = mimetypes.guess_extension(resp.headers.get("Content-Type", "").split(";")[0]) or ".jpg"
            filename = f"{category.slug}{ext}"

            category.image.save(filename, ContentFile(resp.content), save=True)
            self.stdout.write(self.style.SUCCESS(f"  saved as categories/images/{filename}"))
