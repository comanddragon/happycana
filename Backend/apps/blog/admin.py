from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.blog.models import BlogPost
from core.admin_display import image_thumbnail


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = [
        "thumbnail",
        "title",
        "storefront",
        "author",
        "published_at",
        "is_published",
    ]
    list_display_links = ["thumbnail", "title"]
    list_filter = ["is_published"]
    search_fields = ["title", "slug", "author"]
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Image")
    def thumbnail(self, obj):
        return image_thumbnail(obj.image, obj.title)
