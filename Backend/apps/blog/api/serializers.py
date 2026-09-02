import re
from rest_framework import serializers
from apps.blog.models import BlogPost


class BlogPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BlogPost
        # read_time is a plain stored field now (computed once in
        # BlogPost.save()) rather than a SerializerMethodField that read
        # the full content_text on every request — see models.py.
        fields = [
            "slug", "title", "description", "tags",
            "author", "image", "published_at", "updated_at", "read_time",
        ]


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        # content_html is cleaned once at write time (BlogPost.save()), so
        # it's returned as-is here instead of re-running the regex cleanup
        # pipeline on every detail-page request.
        fields = BlogPostListSerializer.Meta.fields + ["content_html", "source_url"]