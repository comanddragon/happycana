import uuid
from django.db import models


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
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
