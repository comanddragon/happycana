import uuid
from django.db import models
from apps.blog.utils import clean_content_html, compute_read_time


class BlogPost(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug           = models.SlugField(max_length=220, unique=True)
    title          = models.CharField(max_length=300)
    description    = models.TextField(blank=True)
    content_html   = models.TextField(blank=True)
    content_text   = models.TextField(blank=True)
    author         = models.CharField(max_length=150, blank=True)
    image          = models.URLField(max_length=500, blank=True)
    tags           = models.JSONField(default=list, blank=True)
    source_url     = models.URLField(max_length=500, blank=True)
    published_at   = models.DateTimeField(null=True, blank=True)
    is_published   = models.BooleanField(default=True)
    # Computed once in save() below from content_text, instead of on every
    # list-view request — see api/serializers.py and the SEO & AEO audit
    # blog-performance notes for why this used to be expensive.
    # db_default keeps a real server-side default so the raw-SQL ingestion
    # path (.scripts/seed_blogs_direct_conn.py, which bypasses save()
    # entirely) can omit this column without violating NOT NULL.
    read_time      = models.CharField(max_length=20, blank=True, default="", db_default="")
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-published_at"]
        indexes = [
            # Every list query filters on is_published and sorts by
            # -published_at (see Meta.ordering above and
            # BlogPostListView.get_queryset) — without this, both require a
            # full table scan + sort that gets slower as posts are scraped
            # in over time.
            models.Index(fields=["is_published", "-published_at"], name="blog_published_idx"),
        ]

    def save(self, *args, **kwargs):
        # Clean HTML and compute read time once, at write time, rather than
        # on every request. clean_content_html() is idempotent, so this is
        # safe to run again on an already-cleaned post (e.g. a re-save from
        # the admin).
        if self.content_html:
            self.content_html = clean_content_html(self.content_html)
        self.read_time = compute_read_time(self.content_text)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
