from rest_framework import generics
from core.permissions import IsAdminOrReadOnly
from apps.blog.models import BlogPost
from .serializers import BlogPostListSerializer, BlogPostDetailSerializer


class BlogPostListView(generics.ListAPIView):
    serializer_class   = BlogPostListSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(generics.RetrieveAPIView):
    serializer_class   = BlogPostDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field        = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
