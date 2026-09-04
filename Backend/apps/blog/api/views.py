from rest_framework import generics
from rest_framework.response import Response
from core.permissions import IsAdminOrReadOnly
from core.cache import get_cached_blog_response, cache_blog_response
from apps.blog.models import BlogPost
from apps.storefronts.querysets import for_request
from .serializers import BlogPostListSerializer, BlogPostDetailSerializer


class BlogPostListView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # content_html/content_text are large scraped-HTML blobs and this
        # serializer never outputs either (read_time is now a stored field,
        # not computed from content_text) — deferring them means each
        # request only pulls what the list actually renders instead of
        # every full article body for every row on the page.
        return for_request(
            BlogPost.objects.filter(is_published=True), self.request
        ).defer("content_html", "content_text")

    def list(self, request, *args, **kwargs):
        cache_key = (
            f"{getattr(request.storefront, 'id', 'legacy')}:{request.get_full_path()}"
        )
        cached = get_cached_blog_response(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache_blog_response(cache_key, response.data)
        return response


class BlogPostDetailView(generics.RetrieveAPIView):
    serializer_class = BlogPostDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return for_request(BlogPost.objects.filter(is_published=True), self.request)

    def retrieve(self, request, *args, **kwargs):
        cache_key = (
            f"{getattr(request.storefront, 'id', 'legacy')}:{request.get_full_path()}"
        )
        cached = get_cached_blog_response(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        cache_blog_response(cache_key, response.data)
        return response
