# =============================================================================
# apps/catalog/api/views.py
# =============================================================================
from rest_framework import generics, filters, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsAdminOrReadOnly
from .serializers import *
from .filters import ProductFilter, ProductVariantFilter, CategoryFilter


class EffectListView(generics.ListAPIView):
    queryset = Effect.objects.all().order_by("name")
    serializer_class = EffectSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_class    = CategoryFilter
    parser_classes     = [MultiPartParser, FormParser]


    def get_queryset(self):
        return Category.objects.root_categories()

    def get_serializer_class(self):
        return CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Category.objects.with_children()
    serializer_class   = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]
    lookup_field = "slug"

class ProductListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class    = ProductFilter


    def get_queryset(self):
        return Product.objects.active().full()

    def get_serializer_class(self):
        return ProductWriteSerializer if self.request.method == "POST" else ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.full()

    def get_serializer_class(self):
        return ProductWriteSerializer if self.request.method in ("PUT", "PATCH") else ProductSerializer


# ------------------------------------------------------------------
# Product Images
# ------------------------------------------------------------------

class ProductImageListView(generics.ListCreateAPIView):
    serializer_class   = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs["product_pk"])


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])


class SetPrimaryImageView(APIView):
    """Marks a specific image as primary, demoting all others."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, product_pk, pk):
        image = ProductImage.objects.get(pk=pk, product_id=product_pk)
        image.is_primary = True
        image.save()
        return Response(ProductImageSerializer(image, context={"request": request}).data)


# ------------------------------------------------------------------
# Product Videos
# ------------------------------------------------------------------

class ProductVideoListView(generics.ListCreateAPIView):
    serializer_class   = ProductVideoSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductVideo.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs["product_pk"])


class ProductVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ProductVideoSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductVideo.objects.filter(product_id=self.kwargs["product_pk"])


class SetPrimaryVideoView(APIView):
    """Marks a specific video as primary, demoting all others."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, product_pk, pk):
        video = ProductVideo.objects.get(pk=pk, product_id=product_pk)
        video.is_primary = True
        video.save()
        return Response(ProductVideoSerializer(video, context={"request": request}).data)

class ProductVariantListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_class    = ProductVariantFilter
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            ProductVariant.objects
            .for_product(self.kwargs["product_pk"])
            .with_attributes()
            .with_stock()
        )

    def get_serializer_class(self):
        return ProductVariantWriteSerializer if self.request.method == "POST" else ProductVariantSerializer

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs["product_pk"])


class ProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ProductVariant.objects.for_product(self.kwargs["product_pk"]).with_attributes()

    def get_serializer_class(self):
        return ProductVariantWriteSerializer if self.request.method in ("PUT", "PATCH") else ProductVariantSerializer

class BrandListView(generics.ListAPIView):
  queryset = Brand.objects.filter(is_active=True)
  serializer_class = BrandSerializer
  permission_classes = [IsAdminOrReadOnly]

class BrandDetailView(generics.RetrieveAPIView):
  queryset = Brand.objects.filter(is_active=True)
  serializer_class = BrandSerializer
  lookup_field = "slug"