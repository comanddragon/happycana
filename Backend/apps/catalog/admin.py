from django.contrib import admin
from apps.catalog.models import Category, Product, ProductVariant, Attribute, ProductImage, ProductVideo, VariantImage, \
    VariantVideo, Effect, Brand, Lab


class AttributeInline(admin.TabularInline):
    model  = Attribute
    extra  = 1
    fields = ["attribute_type", "value"]


class ProductImageInline(admin.TabularInline):
    model          = ProductImage
    extra          = 1
    fields         = ["image", "alt_text", "is_primary", "order"]
    readonly_fields= ["created_at"]

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1
    fields = ["image", "alt_text", "is_primary", "order"]
    readonly_fields = ["created_at"]


class ProductVideoInline(admin.TabularInline):
    model          = ProductVideo
    extra          = 1
    fields         = ["video_type", "file", "external_url", "thumbnail", "title", "is_primary", "order"]
    readonly_fields= ["created_at"]

class VariantVideoInline(admin.TabularInline):
    model          = VariantVideo
    extra          = 1
    fields         = ["video_type", "file", "external_url", "thumbnail", "title", "is_primary", "order"]
    readonly_fields= ["created_at"]


class ProductVariantInline(admin.TabularInline):
    model  = ProductVariant
    extra  = 0
    fields = ["sku", "price", "is_active"]
    show_change_link = True


class LabInline(admin.StackedInline):
    model = Lab
    extra = 0
    fields = [
        "potency", "thc_percent", "thca_percent", "cbd_percent",
        "cbda_percent", "cbn_percent", "cbg_percent", "terpenes",
        "coa_url", "coa_file",
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "parent", "is_active"]
    list_filter   = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = ({"slug": ("name",)})
    fieldsets = (
        (None, {"fields": ("parent", "name", "slug", "description", "image", "is_active")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display  = ["name", "is_active", "website"]
    list_filter   = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "logo_url", "website", "is_active")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug"]
    list_filter   = ["slug"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines         = [ProductImageInline, ProductVideoInline, ProductVariantInline]
    list_display    = ["name", "category_list", "base_price", "is_active", "created_at"]
    list_filter     = ["is_active", "categories", "created_at"]
    search_fields   = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields   = ["categories"]

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(obj.categories.values_list("name", flat=True))


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines       = [LabInline, VariantImageInline, VariantVideoInline, AttributeInline]
    list_display  = ["sku", "product", "price", "is_active"]
    list_filter   = ["is_active"]
    search_fields = ["sku", "product__name"]
    raw_id_fields = ["product"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display   = ["product", "alt_text", "is_primary", "order", "created_at"]
    list_filter    = ["is_primary"]
    search_fields  = ["product__name", "alt_text"]
    raw_id_fields  = ["product"]
    readonly_fields= ["created_at"]


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display   = ["product", "title", "video_type", "is_primary", "order", "created_at"]
    list_filter    = ["video_type", "is_primary"]
    search_fields  = ["product__name", "title"]
    raw_id_fields  = ["product"]
    readonly_fields= ["created_at"]

@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    list_display   = ["variant", "alt_text", "is_primary", "order", "created_at"]
    list_filter    = ["is_primary"]
    search_fields = ["variant__attributes__attribute_type__name", "alt_text"]
    raw_id_fields  = ["variant"]
    readonly_fields= ["created_at"]


@admin.register(VariantVideo)
class VariantVideoAdmin(admin.ModelAdmin):
    list_display   = ["variant", "title", "video_type", "is_primary", "order", "created_at"]
    list_filter    = ["video_type", "is_primary"]
    search_fields = ["variant__attributes__attribute_type__name", "title"]
    raw_id_fields  = ["variant"]
    readonly_fields= ["created_at"]
