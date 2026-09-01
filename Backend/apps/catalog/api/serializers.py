from rest_framework import serializers
from apps.catalog.models import (
    Category, Product, ProductVariant, Brand, Effect, Lab,
    Attribute, AttributeType,
    ProductImage, ProductVideo, VariantImage, VariantVideo,
)

class CategorySerializer(serializers.ModelSerializer):
    children  = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = [
            "id", "parent", "name", "slug", "description", "image", "image_url",
            "is_active", "children", "meta_title", "meta_description",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"write_only": True}}


    def get_children(self, obj):
        # attach_full_tree() (called from the view) stamps this in memory
        # so no query is issued here. Fall back to a live query only if a
        # caller serializes a Category without going through that path.
        children = getattr(obj, "_prefetched_children", None)
        if children is None:
            children = [c for c in obj.children.all() if c.is_active]
        else:
            children = [c for c in children if c.is_active]
        if not children:
            return []
        return CategorySerializer(children, many=True, context=self.context).data

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class CategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["id", "name", "slug"]


class AttributeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="attribute_type.name", read_only=True)

    class Meta:
        model  = Attribute
        fields = ["id", "name", "value"]
        read_only_fields = ["id"]

class EffectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Effect
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]

class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lab
        fields = [
            "potency", "thc_percent", "thca_percent", "cbd_percent",
            "cbda_percent", "cbn_percent", "cbg_percent", "terpenes",
            "coa_url",
        ]

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "source_url", "image_url", "alt_text", "is_primary", "order"]
        read_only_fields = ["id"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return obj.source_url or None

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Brand
        fields = [
            "id", "name", "slug", "description", "logo_url", "website",
            "meta_title", "meta_description",
        ]
        read_only_fields = ["id"]


class BrandMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Brand
        fields = ["id", "name", "slug", "logo_url"]

class ProductVideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    playback_url  = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVideo
        fields = [
            "id", "video_type", "file", "external_url",
            "thumbnail", "thumbnail_url", "title",
            "is_primary", "order", "playback_url",
        ]
        read_only_fields = ["id"]

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_playback_url(self, obj):
        request = self.context.get("request")
        if obj.video_type == ProductVideo.VideoType.UPLOAD and obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.external_url

class VariantImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = VariantImage
        fields = ["id", "image", "image_url", "alt_text", "is_primary", "order"]
        read_only_fields = ["id"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

class VariantVideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    playback_url  = serializers.SerializerMethodField()

    class Meta:
        model  = VariantVideo
        fields = [
            "id", "video_type", "file", "external_url",
            "thumbnail", "thumbnail_url", "title",
            "is_primary", "order", "playback_url",
        ]
        read_only_fields = ["id"]

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_playback_url(self, obj):
        request = self.context.get("request")
        if obj.video_type == VariantVideo.VideoType.UPLOAD and obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.external_url

class ProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug"]

class ProductVariantSerializer(serializers.ModelSerializer):
    attributes    = AttributeSerializer(many=True, read_only=True)
    images        = VariantImageSerializer(many=True, read_only=True)
    videos        = VariantVideoSerializer(many=True, read_only=True)
    primary_image = VariantImageSerializer(read_only=True)
    primary_video = VariantVideoSerializer(read_only=True)
    product = ProductMinimalSerializer(read_only=True)
    lab = LabSerializer(read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVariant
        fields = [
            "id", "sku", "price", "is_active",
            "product", "attributes",
            "primary_image", "primary_video",
            "images", "videos", "weight_value",
            "weight_unit", "lab", "in_stock",
        ]
        read_only_fields = ["id"]

    def get_in_stock(self, obj):
        # Relies on the queryset prefetching stock_levels (see
        # ProductQuerySet.with_stock / .full()) — falls back to a live
        # query if a caller serializes a variant without that prefetch.
        return any((sl.quantity - sl.reserved) > 0 for sl in obj.stock_levels.all())


class ProductVariantWriteSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model  = ProductVariant
        fields = ["sku", "price", "image", "is_active", "attributes"]

    def create(self, validated_data):
        attrs = validated_data.pop("attributes", [])
        variant = ProductVariant.objects.create(**validated_data)
        objs = []
        for a in attrs:
            attr_type, _ = AttributeType.objects.get_or_create(name=a["name"])
            objs.append(Attribute(variant=variant, attribute_type=attr_type, value=a["value"]))
        Attribute.objects.bulk_create(objs)
        return variant


class LabSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lab
        fields = ["potency", "thc_percent"]


class ProductVariantSummarySerializer(serializers.ModelSerializer):
    """Just what the product grid needs (price, weight, THC, and an id to
    add to cart) — no attributes/images/videos, unlike ProductVariantSerializer."""
    lab = LabSummarySerializer(read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVariant
        fields = ["id", "price", "weight_value", "weight_unit", "lab", "in_stock"]
        read_only_fields = ["id"]

    def get_in_stock(self, obj):
        # See ProductVariantSerializer.get_in_stock — same prefetch dependency.
        return any((sl.quantity - sl.reserved) > 0 for sl in obj.stock_levels.all())


class ProductListSerializer(serializers.ModelSerializer):
    """Lean serializer for the product grid: no nested images/videos on
    variants, since the grid only renders name/price/primary image/brand/category/THC."""
    category      = CategoryMinimalSerializer(read_only=True)
    brand         = BrandMinimalSerializer(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    effects       = EffectSerializer(many=True, read_only=True)
    variants      = ProductVariantSummarySerializer(many=True, read_only=True)

    class Meta:
        model  = Product
        fields = [
            "id", "category", "name", "slug",
            "base_price", "is_active", "created_at",
            "primary_image", "brand", "compliance_category",
            "cannabis_type", "sub_type", "is_featured", "is_new",
            "effects", "variants",
        ]
        read_only_fields = ["id", "slug", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category      = CategoryMinimalSerializer(read_only=True)
    variants      = ProductVariantSerializer(many=True, read_only=True)
    images        = ProductImageSerializer(many=True, read_only=True)
    videos        = ProductVideoSerializer(many=True, read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    primary_video = ProductVideoSerializer(read_only=True)
    brand = BrandMinimalSerializer(read_only=True)
    effects = EffectSerializer(many=True, read_only=True)

    class Meta:
        model  = Product
        fields = [
            "id", "category", "name", "slug", "description",
            "meta_title", "meta_description",
            "base_price", "is_active", "created_at",
            "primary_image", "primary_video",
            "images", "videos", "variants",
            "brand", "compliance_category", "cannabis_type", "sub_type",
            "is_featured", "is_new", "effects"
        ]
        read_only_fields = ["id", "slug", "created_at"]


class ProductWriteSerializer(serializers.ModelSerializer):
    brand   = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False, allow_null=True)
    effects = serializers.PrimaryKeyRelatedField(queryset=Effect.objects.all(), many=True, required=False)

    class Meta:
        model  = Product
        fields = ["category", "name", "description", "base_price", "is_active"]


class LabResultProductSerializer(serializers.ModelSerializer):
    """Just what the public Lab Results index needs to display and link
    back to the product — leaner than ProductSerializer/ProductListSerializer."""
    brand         = BrandMinimalSerializer(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)

    class Meta:
        model  = Product
        fields = ["id", "name", "slug", "cannabis_type", "compliance_category", "brand", "primary_image"]


class LabResultSerializer(serializers.ModelSerializer):
    """One row per variant that carries a real, on-file Lab record with a
    certificate of analysis — powers the public /catalog/labs/ endpoint
    (a verifiable-trust page: every row here links to an actual COA)."""
    product = LabResultProductSerializer(read_only=True)
    lab     = LabSerializer(read_only=True)

    class Meta:
        model  = ProductVariant
        fields = ["id", "sku", "weight_value", "weight_unit", "product", "lab"]
        read_only_fields = ["id"]

