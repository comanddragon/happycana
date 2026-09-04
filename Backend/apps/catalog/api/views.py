from rest_framework import generics, filters, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsAdminOrReadOnly
from core.cache import cache_category_tree_response, get_cached_category_tree_response
from apps.catalog.models import (
    Brand,
    Category,
    Effect,
    Listing,
    Product,
    ProductDiscount,
    ProductImage,
    ProductVariant,
    ProductVideo,
)
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    CollectionSerializer,
    EffectSerializer,
    LabResultSerializer,
    ListingSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ProductVariantWriteSerializer,
    ProductVideoSerializer,
    ProductWriteSerializer,
)
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

    def list(self, request, *args, **kwargs):
        # The tree only changes when a category is written (see
        # apps.catalog.signals), which is rare — cache the assembled
        # response per path+querystring instead of walking/serializing
        # the whole active tree on every storefront request.
        cache_key = request.get_full_path()
        cached = get_cached_category_tree_response(cache_key)
        if cached is not None:
            return Response(cached)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        objs = page if page is not None else list(queryset)
        # See CategoryManager.attach_full_tree: without this, the
        # recursive serializer issues one query per category at every
        # depth below root->children.
        Category.objects.attach_full_tree(objs)
        serializer = self.get_serializer(objs, many=True)
        response_data = self.get_paginated_response(serializer.data).data if page is not None else serializer.data
        cache_category_tree_response(cache_key, response_data)
        return Response(response_data)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser]
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Category.objects.attach_full_tree([instance])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CollectionQuerysetMixin:
    """Collections are active, root-level categories not marked as key."""

    def get_queryset(self):
        return (
            Category.objects.filter(is_active=True, is_key=False, parent__isnull=True)
            .annotate(
                product_count=Count(
                    "products",
                    filter=Q(products__is_active=True),
                    distinct=True,
                )
            )
            .order_by("name", "id")
        )


class CollectionListView(CollectionQuerysetMixin, generics.ListAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class CollectionDetailView(CollectionQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

class ProductListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class    = ProductFilter

    def get_queryset(self):
        if self.request.method == "POST":
            return Product.objects.active().full()
        # List only needs what ProductListSerializer renders — .full() was
        # additionally pulling variant attributes/images/videos for every
        # product on every page, none of which the grid displays. Stock is
        # prefetched on its own (cheap, one extra query) so the grid can
        # show accurate in_stock without an N+1.
        return (
            Product.objects.active()
            .with_category().with_images()
            .select_related("brand")
            .prefetch_related(
                "effects", "variants__lab", "variants__stock_levels",
                Prefetch("discounts", queryset=ProductDiscount.objects.filter(is_active=True), to_attr="_prefetched_discounts"),
            )
        )

    def get_serializer_class(self):
        return ProductWriteSerializer if self.request.method == "POST" else ProductListSerializer


class CollectionProductListView(ProductListView):
    """Filtered product listing scoped to one public collection."""

    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        # Resolve through the collection queryset so key categories and
        # inactive categories return 404 instead of masquerading as collections.
        collection = generics.get_object_or_404(
            Category.objects.filter(is_active=True, is_key=False, parent__isnull=True),
            slug=self.kwargs["slug"],
        )
        return super().get_queryset().filter(categories=collection).distinct()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.full().prefetch_related(
            Prefetch("discounts", queryset=ProductDiscount.objects.filter(is_active=True), to_attr="_prefetched_discounts")
        )

    def get_serializer_class(self):
        return ProductWriteSerializer if self.request.method in ("PUT", "PATCH") else ProductSerializer


class StorefrontRequiredMixin:
    def get_storefront(self):
        storefront = getattr(self.request, "storefront", None)
        if storefront is None:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"storefront": "Select a storefront with X-Storefront or a configured origin/domain."})
        return storefront


class StorefrontListingQuerysetMixin(StorefrontRequiredMixin):
    queryset = Listing.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return (
            Listing.objects.filter(storefront=self.get_storefront(), is_active=True)
            .select_related("product", "product__brand")
            .prefetch_related(
                "product__categories", "product__images", "product__effects",
                "product__variants__lab", "product__variants__stock_levels",
            )
        )


class ListingListView(StorefrontListingQuerysetMixin, generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]


class ListingDetailView(StorefrontListingQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


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
  permission_classes = [IsAdminOrReadOnly]
  lookup_field = "slug"


class LabResultListView(generics.ListAPIView):
    """Public, read-only list of every variant with a real, on-file
    certificate of analysis — backs the /learn/lab-results index page so
    the site's lab-testing claims are independently checkable rather than
    just a badge graphic on the homepage."""
    serializer_class    = LabResultSerializer
    permission_classes  = [IsAdminOrReadOnly]
    filter_backends     = [filters.OrderingFilter]
    ordering_fields      = ["product__name", "sku"]
    ordering            = ["product__name"]

    def get_queryset(self):
        return (
            ProductVariant.objects.with_coa()
            .select_related("product", "product__brand", "lab")
            .prefetch_related("product__images")
        )
