from django.contrib import admin
from apps.blog.models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display   = ["title", "slug", "author", "published_at", "is_published"]
    list_filter    = ["is_published"]
    search_fields  = ["title", "slug", "author"]
    prepopulated_fields = {"slug": ("title",)}
