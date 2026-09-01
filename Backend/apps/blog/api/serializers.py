import re
from rest_framework import serializers
from apps.blog.models import BlogPost

WORDS_PER_MINUTE = 200


def _read_time(text: str) -> str:
    words = len(re.findall(r"\S+", text or ""))
    minutes = max(1, round(words / WORDS_PER_MINUTE))
    return f"{minutes} min"


class BlogPostListSerializer(serializers.ModelSerializer):
    read_time = serializers.SerializerMethodField()

    class Meta:
        model  = BlogPost
        fields = [
            "slug", "title", "description", "tags",
            "author", "image", "published_at", "read_time",
        ]

    def get_read_time(self, obj):
        return _read_time(obj.content_text)


class BlogPostDetailSerializer(BlogPostListSerializer):
    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ["content_html", "source_url"]
