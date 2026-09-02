# =============================================================================
# apps/blog/management/commands/backfill_blog_metadata.py
# =============================================================================
# One-time backfill for posts that existed before BlogPost.save() started
# computing `read_time` and cleaning `content_html` automatically (see
# models.py). Safe to re-run — both operations are idempotent.
#
# Run after applying migration 0002_blogpost_read_time_and_index, ideally
# off-peak: this touches every row and, per the SEO & AEO audit's
# blog-performance notes, this table may currently be large enough that a
# naive full-table pass is itself slow.
from django.core.management.base import BaseCommand
from apps.blog.models import BlogPost


class Command(BaseCommand):
    help = "Backfill read_time and cleaned content_html for existing BlogPost rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size", type=int, default=200,
            help="Rows to process per batch (default: 200).",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        qs = BlogPost.objects.all().only("id", "content_html", "content_text", "read_time")

        total = qs.count()
        updated = 0
        batch = []

        def flush(batch):
            for post in batch:
                # Reuses BlogPost.save()'s own cleaning/read_time logic
                # rather than duplicating it here — see models.py.
                post.save(update_fields=["content_html", "read_time"])

        for post in qs.iterator(chunk_size=batch_size):
            batch.append(post)
            if len(batch) >= batch_size:
                flush(batch)
                updated += len(batch)
                self.stdout.write(f"  ...{updated}/{total}")
                batch = []

        if batch:
            flush(batch)
            updated += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Backfilled {updated} blog post(s)."))
