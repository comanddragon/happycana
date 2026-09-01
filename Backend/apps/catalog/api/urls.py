# =============================================================================
# apps/catalog/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("catalog/effects/", views.EffectListView.as_view(), name="effect-list"),
    path("catalog/categories/",                                          views.CategoryListView.as_view(),          name="category-list"),
    path("catalog/categories/<slug:slug>/",                               views.CategoryDetailView.as_view(),        name="category-detail"),
    path("catalog/products/",                                            views.ProductListView.as_view(),           name="product-list"),
    path("catalog/products/<slug:slug>/",                                 views.ProductDetailView.as_view(),         name="product-detail"),
    path("products/<uuid:product_pk>/images/",                       views.ProductImageListView.as_view(),      name="product-image-list"),
    path("products/<uuid:product_pk>/images/<uuid:pk>/",             views.ProductImageDetailView.as_view(),    name="product-image-detail"),
    path("products/<uuid:product_pk>/images/<uuid:pk>/set-primary/", views.SetPrimaryImageView.as_view(),       name="product-image-set-primary"),
    path("products/<uuid:product_pk>/videos/", views.ProductVideoListView.as_view(), name="product-video-list"),
    path("products/<uuid:product_pk>/videos/<uuid:pk>/", views.ProductVideoDetailView.as_view(),    name="product-video-detail"),
    path("products/<uuid:product_pk>/videos/<uuid:pk>/set-primary/", views.SetPrimaryVideoView.as_view(),   name="product-video-set-primary"),
    path("catalog/products/<uuid:product_pk>/variants/",                views.ProductVariantListView.as_view(),    name="variant-list"),
    path("catalog/products/<uuid:product_pk>/variants/<uuid:pk>/",      views.ProductVariantDetailView.as_view(),  name="variant-detail"),
    path("catalog/brands/", views.BrandListView.as_view(), name="brand-list"),
    path("catalog/brands/<slug:slug>/", views.BrandDetailView.as_view(), name="brand-detail"),
    path("catalog/labs/", views.LabResultListView.as_view(), name="lab-result-list"),

]