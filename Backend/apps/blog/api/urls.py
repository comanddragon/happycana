from django.urls import path
from . import views

urlpatterns = [
    path("blog/posts/",             views.BlogPostListView.as_view(),   name="blog-post-list"),
    path("blog/posts/<slug:slug>/", views.BlogPostDetailView.as_view(), name="blog-post-detail"),
]
