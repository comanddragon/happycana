import re
from rest_framework import serializers
from apps.blog.models import BlogPost

WORDS_PER_MINUTE = 200

_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_DATA_SRC_RE = re.compile(r'data-src="([^"]*)"')
_DATA_SRCSET_RE = re.compile(r'data-srcset="([^"]*)"')
_HAS_SRC_RE = re.compile(r'(?<!data-)\bsrc="')
_HAS_SRCSET_RE = re.compile(r'(?<!data-)\bsrcset="')
_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_LINK_RE = re.compile(r"<link\b[^>]*/?>", re.IGNORECASE)
_STORE_HREF_RE = re.compile(r'href="/collections/?"')


def _fix_lazy_image(match: "re.Match[str]") -> str:
    tag = match.group(0)

    if not _HAS_SRC_RE.search(tag):
        src_match = _DATA_SRC_RE.search(tag)
        if src_match:
            tag = tag.replace("<img", f'<img src="{src_match.group(1)}"', 1)

    if not _HAS_SRCSET_RE.search(tag):
        srcset_match = _DATA_SRCSET_RE.search(tag)
        if srcset_match:
            tag = tag.replace("<img", f'<img srcset="{srcset_match.group(1)}"', 1)

    return tag


def _clean_content_html(html: str) -> str:
    if not html:
        return html
    html = _SCRIPT_RE.sub("", html)
    html = _LINK_RE.sub("", html)
    html = _IMG_TAG_RE.sub(_fix_lazy_image, html)
    html = _STORE_HREF_RE.sub('href="/shop"', html)
    return html


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
    content_html = serializers.SerializerMethodField()

    class Meta(BlogPostListSerializer.Meta):
        fields = BlogPostListSerializer.Meta.fields + ["content_html", "source_url"]

    def get_content_html(self, obj):
        return _clean_content_html(obj.content_html)