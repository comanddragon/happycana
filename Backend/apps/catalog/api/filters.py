# =============================================================================
# apps/catalog/api/filters.py
# =============================================================================
import django_filters
from django.db.models import Q
from apps.catalog.models import Product, ProductVariant, Category


class ProductFilter(django_filters.FilterSet):
    """
    Supports the following query params on GET /api/v1/products/:

        ?category=<uuid>
        ?category_slug=shoes
        ?min_price=10&max_price=250
        ?in_stock=true
        ?is_active=true
        ?search=running+shoes          # name, description, SKU
        ?has_variant_attribute=Color   # products with a specific attribute name
        ?ordering=base_price           # base_price | -base_price | created_at | name
    """

    # -- Category --
    category = django_filters.CharFilter(
        field_name="category__slug",
        lookup_expr="iexact",
        label="Filter by category slug",
    )

    # -- Price range --
    min_price = django_filters.NumberFilter(
        field_name="base_price",
        lookup_expr="gte",
        label="Minimum price",
    )
    max_price = django_filters.NumberFilter(
        field_name="base_price",
        lookup_expr="lte",
        label="Maximum price",
    )

    # -- Availability --
    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock",
        label="Only show in-stock products",
    )

    # -- Status --
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Active products only",
    )

    # -- Full-text search fallback (ORM) --
    search = django_filters.CharFilter(
        method="filter_search",
        label="Search by name, description, or SKU",
    )

    # -- Attribute filter --
    has_variant_attribute = django_filters.CharFilter(
        method="filter_by_attribute_name",
        label="Filter products that have a variant with this attribute name",
    )
    attribute_value = django_filters.CharFilter(
        method="filter_by_attribute_value",
        label="Filter products whose variant attribute matches this value (use with has_variant_attribute)",
    )

    # -- Ordering --
    ordering = django_filters.OrderingFilter(
        fields=(
            ("base_price",  "base_price"),
            ("created_at",  "created_at"),
            ("name",        "name"),
        ),
        label="Sort results",
    )
    brand = django_filters.CharFilter(
        field_name="brand__slug", lookup_expr="iexact", label="Filter by brand slug",
    )
    compliance_category = django_filters.CharFilter(
        field_name="compliance_category", lookup_expr="iexact",
    )
    cannabis_type = django_filters.CharFilter(
        field_name="cannabis_type", lookup_expr="iexact",
    )
    effect = django_filters.CharFilter(
        method="filter_effect", label="Products with this effect, e.g. ?effect=relaxed",
    )
    min_thc = django_filters.NumberFilter(
        field_name="variants__lab__thc_percent", lookup_expr="gte",
    )
    max_thc = django_filters.NumberFilter(
        field_name="variants__lab__thc_percent", lookup_expr="lte",
    )

    class Meta:
        model  = Product
        fields = [
            "category", "effect",
            "min_price", "max_price",
            "in_stock", "is_active",
            "search", "min_thc", "max_thc",
            "has_variant_attribute", "attribute_value",
            "brand", "compliance_category", "cannabis_type",

        ]

    # ------------------------------------------------------------------
    # Custom filter methods
    # ------------------------------------------------------------------

    def filter_effect(self, queryset, name, value):
        return queryset.filter(effects__slug__iexact=value).distinct()

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.in_stock()      # delegates to ProductManager
        if value is False:
            return queryset.out_of_stock()
        return queryset

    def filter_search(self, queryset, name, value):
        """
        ORM fallback search. For production traffic use
        SearchService.search_products() at the view level instead.
        """
        return queryset.filter(
            Q(name__icontains=value)        |
            Q(description__icontains=value) |
            Q(variants__sku__icontains=value)
        ).distinct()

    def filter_by_attribute_name(self, queryset, name, value):
        return queryset.filter(variants__attributes__attribute_type__name__iexact=value).distinct()

    def filter_by_attribute_value(self, queryset, name, value):
        """
        Pairs with has_variant_attribute.
        ?has_variant_attribute=Color&attribute_value=Red
        returns all products that have a Red Color variant.
        """
        return queryset.filter(
            variants__attributes__value__iexact=value
        ).distinct()


# =============================================================================
# apps/catalog/api/filters.py (continued)
# =============================================================================

class ProductVariantFilter(django_filters.FilterSet):
    """
    Supports the following query params on GET /api/v1/products/<id>/variants/:

        ?min_price=10&max_price=100
        ?is_active=true
        ?in_stock=true
        ?attribute_name=Color&attribute_value=Red
    """

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    in_stock  = django_filters.BooleanFilter(
        method="filter_in_stock",
        label="Only show variants with available stock",
    )

    attribute_name  = django_filters.CharFilter(
        method="filter_attribute_name",
        label="Filter by attribute name e.g. Color",
    )
    attribute_value = django_filters.CharFilter(
        method="filter_attribute_value",
        label="Filter by attribute value e.g. Red",
    )

    class Meta:
        model  = ProductVariant
        fields = ["min_price", "max_price", "is_active", "in_stock", "attribute_name", "attribute_value"]

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.available()    # delegates to ProductVariantManager
        return queryset

    def filter_attribute_name(self, queryset, name, value):
        return queryset.filter(attributes__attribute_type__name__iexact=value).distinct()

    def filter_attribute_value(self, queryset, name, value):
        return queryset.filter(attributes__value__iexact=value).distinct()


class CategoryFilter(django_filters.FilterSet):
    """
    Supports the following query params on GET /api/v1/categories/:

        ?is_active=true
        ?parent=<uuid>
        ?root_only=true        # top-level categories only
    """

    is_active = django_filters.BooleanFilter(field_name="is_active")
    parent    = django_filters.UUIDFilter(field_name="parent__id")
    root_only = django_filters.BooleanFilter(
        method="filter_root_only",
        label="Return only root (parentless) categories",
    )

    class Meta:
        model  = Category
        fields = ["is_active", "parent", "root_only"]

    def filter_root_only(self, queryset, name, value):
        if value is True:
            return queryset.filter(parent__isnull=True)
        return queryset