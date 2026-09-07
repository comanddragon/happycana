from django.contrib import admin
from django.db.models import Prefetch
from unfold.admin import ModelAdmin

from apps.catalog.models import (
    Attribute,
    Brand,
    Category,
    Effect,
    Lab,
    Product,
    ProductImage,
    ProductVariant,
    ProductVideo,
    VariantImage,
    VariantVideo,
)
from core.admin_display import image_thumbnail


class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 1
    fields = ["attribute_type", "value"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "is_primary", "order"]
    readonly_fields = ["created_at"]


class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1
    fields = ["image", "alt_text", "is_primary", "order"]
    readonly_fields = ["created_at"]


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    fields = [
        "video_type",
        "file",
        "external_url",
        "thumbnail",
        "title",
        "is_primary",
        "order",
    ]
    readonly_fields = ["created_at"]


class VariantVideoInline(admin.TabularInline):
    model = VariantVideo
    extra = 1
    fields = [
        "video_type",
        "file",
        "external_url",
        "thumbnail",
        "title",
        "is_primary",
        "order",
    ]
    readonly_fields = ["created_at"]


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ["sku", "price", "is_active"]
    show_change_link = True


class LabInline(admin.StackedInline):
    model = Lab
    extra = 0
    fields = [
        "potency",
        "thc_percent",
        "thca_percent",
        "cbd_percent",
        "cbda_percent",
        "cbn_percent",
        "cbg_percent",
        "terpenes",
        "coa_url",
        "coa_file",
    ]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["thumbnail", "name", "parent", "is_active"]
    list_display_links = ["thumbnail", "name"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (
            None,
            {"fields": ("parent", "name", "slug", "description", "image", "is_active")},
        ),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )

    @admin.display(description="Image")
    def thumbnail(self, obj):
        url = obj.image.url if obj.image else ""
        return image_thumbnail(url, obj.name)


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ["name", "is_active", "website"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "logo_url",
                    "website",
                    "is_active",
                )
            },
        ),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(Effect)
class EffectAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    list_filter = ["slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductImageInline, ProductVideoInline, ProductVariantInline]
    list_display = [
        "thumbnail",
        "name",
        "category_list",
        "base_price",
        "is_active",
        "created_at",
    ]
    list_display_links = ["thumbnail", "name"]
    list_filter = ["is_active", "categories", "created_at"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["categories"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "categories",
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.order_by(
                        "-is_primary", "order", "created_at"
                    ),
                    to_attr="_admin_images",
                ),
            )
        )

    @admin.display(description="Image")
    def thumbnail(self, obj):
        image = next(
            (item for item in obj._admin_images if item.image or item.source_url),
            None,
        )
        url = (
            image.image.url
            if image and image.image
            else image.source_url
            if image
            else ""
        )
        return image_thumbnail(url, obj.name)

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(category.name for category in obj.categories.all())


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    inlines = [LabInline, VariantImageInline, VariantVideoInline, AttributeInline]
    list_display = ["product", "sku", "price", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["sku", "product__name"]
    raw_id_fields = ["product"]


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ["product", "alt_text", "is_primary", "order", "created_at"]
    list_filter = ["is_primary"]
    search_fields = ["product__name", "alt_text"]
    raw_id_fields = ["product"]
    readonly_fields = ["created_at"]


@admin.register(ProductVideo)
class ProductVideoAdmin(ModelAdmin):
    list_display = [
        "product",
        "title",
        "video_type",
        "is_primary",
        "order",
        "created_at",
    ]
    list_filter = ["video_type", "is_primary"]
    search_fields = ["product__name", "title"]
    raw_id_fields = ["product"]
    readonly_fields = ["created_at"]


@admin.register(VariantImage)
class VariantImageAdmin(ModelAdmin):
    list_display = ["variant", "alt_text", "is_primary", "order", "created_at"]
    list_filter = ["is_primary"]
    search_fields = ["variant__attributes__attribute_type__name", "alt_text"]
    raw_id_fields = ["variant"]
    readonly_fields = ["created_at"]


@admin.register(VariantVideo)
class VariantVideoAdmin(ModelAdmin):
    list_display = [
        "variant",
        "title",
        "video_type",
        "is_primary",
        "order",
        "created_at",
    ]
    list_filter = ["video_type", "is_primary"]
    search_fields = ["variant__attributes__attribute_type__name", "title"]
    raw_id_fields = ["variant"]
    readonly_fields = ["created_at"]
