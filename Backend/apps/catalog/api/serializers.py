from rest_framework import serializers
from apps.catalog.models import (
    Category, Product, ProductVariant, Brand, Effect, Lab,
    Attribute, AttributeType,
    ProductImage, ProductVideo, VariantImage, VariantVideo,
    ProductDiscount,
    Listing,
)
from django.utils import timezone
from apps.catalog_cannabis.models import CannabisProfile
from apps.catalog_peptides.models import PeptideProfile
from apps.catalog_footwear.models import FootwearProfile

class CategorySerializer(serializers.ModelSerializer):
    children  = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = [
            "id", "parent", "name", "slug", "description", "image", "image_url",
            "is_active", "is_key", "children", "meta_title", "meta_description",
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
        fields = ["id", "name", "slug", "is_key"]


class CollectionSerializer(serializers.ModelSerializer):
    """Public representation of a non-key storefront category."""

    image_url = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "image_url",
            "product_count", "meta_title", "meta_description",
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


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


class CannabisProfileSerializer(serializers.ModelSerializer):
    effects = EffectSerializer(source="effect_tags", many=True, read_only=True)

    class Meta:
        model = CannabisProfile
        fields = [
            "compliance_category", "cannabis_type", "sub_type", "thc_percent",
            "cbd_percent", "terpenes", "effects", "coa_url",
        ]
        read_only_fields = fields


class PeptideProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeptideProfile
        fields = [
            "sequence", "molecular_weight", "purity_percent", "form",
            "concentration", "storage_requirements", "documentation_url",
        ]
        read_only_fields = fields


class FootwearProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootwearProfile
        fields = [
            "model_name", "style_code", "release_date", "size_system", "condition",
            "authenticity_status", "box_condition",
        ]
        read_only_fields = fields


def serialize_vertical_profile(product):
    serializers_by_kind = {
        Product.Kind.CANNABIS: ("cannabis_profile", CannabisProfileSerializer),
        Product.Kind.PEPTIDE: ("peptide_profile", PeptideProfileSerializer),
        Product.Kind.FOOTWEAR: ("footwear_profile", FootwearProfileSerializer),
    }
    config = serializers_by_kind.get(product.kind)
    if config is None:
        return None
    relation_name, serializer_class = config
    profile = getattr(product, relation_name, None)
    if profile is None:
        return None
    return {"kind": product.kind, "data": serializer_class(profile).data}

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
        fields = ["sku", "price", "is_active", "attributes"]

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
        fields = ["potency", "thc_percent", "terpenes", "coa_url"]


class ProductVariantSummarySerializer(serializers.ModelSerializer):
    """Just what the product grid needs (price, weight, THC, and an id to
    add to cart) — no attributes/images/videos, unlike ProductVariantSerializer."""
    lab = LabSummarySerializer(read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model  = ProductVariant
        fields = ["id", "sku", "price", "weight_value", "weight_unit", "lab", "in_stock"]
        read_only_fields = ["id"]

    def get_in_stock(self, obj):
        # See ProductVariantSerializer.get_in_stock — same prefetch dependency.
        return any((sl.quantity - sl.reserved) > 0 for sl in obj.stock_levels.all())


class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = ["discount_type", "value"]


def current_discount(product):
    now = timezone.now()
    weekday = (now.weekday() + 1) % 7  # Model convention: Sunday=0.
    discounts = getattr(product, "_prefetched_discounts", None)
    if discounts is None:
        discounts = product.discounts.all()
    valid = [
        discount for discount in discounts
        if discount.is_active
        and (discount.starts_at is None or discount.starts_at <= now)
        and (discount.ends_at is None or discount.ends_at >= now)
        and (not discount.days_of_week or weekday in discount.days_of_week)
    ]
    return max(valid, key=lambda item: item.value) if valid else None


class ProductListSerializer(serializers.ModelSerializer):
    """Lean serializer for the product grid: no nested images/videos on
    variants, since the grid only renders name/price/primary image/brand/category/THC."""
    category      = CategoryMinimalSerializer(many=True, read_only=True, source="categories")
    brand         = BrandMinimalSerializer(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    compliance_category = serializers.SerializerMethodField()
    cannabis_type = serializers.SerializerMethodField()
    sub_type = serializers.SerializerMethodField()
    effects = serializers.SerializerMethodField()
    variants      = ProductVariantSummarySerializer(many=True, read_only=True)
    active_discount = serializers.SerializerMethodField()
    vertical_profile = serializers.SerializerMethodField()

    def get_active_discount(self, obj):
        discount = current_discount(obj)
        return ProductDiscountSerializer(discount).data if discount else None

    def _cannabis_profile(self, obj):
        return getattr(obj, "cannabis_profile", None)

    def get_compliance_category(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.compliance_category if profile else ""

    def get_cannabis_type(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.cannabis_type if profile else ""

    def get_sub_type(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.sub_type if profile else ""

    def get_effects(self, obj):
        profile = self._cannabis_profile(obj)
        return EffectSerializer(profile.effect_tags.all(), many=True).data if profile else []

    def get_vertical_profile(self, obj):
        return serialize_vertical_profile(obj)

    class Meta:
        model  = Product
        fields = [
            "id", "category", "name", "slug",
            "base_price", "compare_at_price", "is_active", "created_at", "updated_at",
            "primary_image", "brand", "compliance_category",
            "cannabis_type", "sub_type", "is_featured", "is_new",
            "effects", "variants", "active_discount", "vertical_profile",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    category      = CategoryMinimalSerializer(many=True, read_only=True, source="categories")
    variants      = ProductVariantSerializer(many=True, read_only=True)
    images        = ProductImageSerializer(many=True, read_only=True)
    videos        = ProductVideoSerializer(many=True, read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    primary_video = ProductVideoSerializer(read_only=True)
    brand = BrandMinimalSerializer(read_only=True)
    compliance_category = serializers.SerializerMethodField()
    cannabis_type = serializers.SerializerMethodField()
    sub_type = serializers.SerializerMethodField()
    effects = serializers.SerializerMethodField()
    active_discount = serializers.SerializerMethodField()
    vertical_profile = serializers.SerializerMethodField()

    def get_active_discount(self, obj):
        discount = current_discount(obj)
        return ProductDiscountSerializer(discount).data if discount else None

    def _cannabis_profile(self, obj):
        return getattr(obj, "cannabis_profile", None)

    def get_compliance_category(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.compliance_category if profile else ""

    def get_cannabis_type(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.cannabis_type if profile else ""

    def get_sub_type(self, obj):
        profile = self._cannabis_profile(obj)
        return profile.sub_type if profile else ""

    def get_effects(self, obj):
        profile = self._cannabis_profile(obj)
        return EffectSerializer(profile.effect_tags.all(), many=True).data if profile else []

    def get_vertical_profile(self, obj):
        return serialize_vertical_profile(obj)

    class Meta:
        model  = Product
        fields = [
            "id", "category", "name", "slug", "description",
            "meta_title", "meta_description",
            "base_price", "compare_at_price", "is_active", "created_at",
            "primary_image", "primary_video",
            "images", "videos", "variants",
            "brand", "compliance_category", "cannabis_type", "sub_type",
            "is_featured", "is_new", "effects", "active_discount", "vertical_profile"
        ]
        read_only_fields = ["id", "slug", "created_at"]


class ProductWriteSerializer(serializers.ModelSerializer):
    brand   = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False, allow_null=True)
    effects = serializers.PrimaryKeyRelatedField(queryset=Effect.objects.all(), many=True, required=False)

    class Meta:
        model  = Product
        fields = [
            "categories", "name", "description", "base_price", "is_active",
            "brand", "effects",
        ]

    def _save_effects(self, product, effects):
        from apps.catalog_cannabis.models import CannabisProfile

        profile, _ = CannabisProfile.objects.get_or_create(product=product)
        profile.effect_tags.set(effects)
        if product.kind != Product.Kind.CANNABIS:
            product.kind = Product.Kind.CANNABIS
            product.save(update_fields=["kind"])

    def create(self, validated_data):
        effects = validated_data.pop("effects", None)
        product = super().create(validated_data)
        if effects is not None:
            self._save_effects(product, effects)
        return product

    def update(self, instance, validated_data):
        effects = validated_data.pop("effects", None)
        product = super().update(instance, validated_data)
        if effects is not None:
            self._save_effects(product, effects)
        return product


class ListingSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    categories = CategoryMinimalSerializer(many=True, read_only=True)
    effective_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id", "slug", "display_name", "effective_price",
            "compare_at_price_override", "is_featured", "meta_title",
            "meta_description", "categories", "product",
        ]
        read_only_fields = fields


class LabResultProductSerializer(serializers.ModelSerializer):
    """Just what the public Lab Results index needs to display and link
    back to the product — leaner than ProductSerializer/ProductListSerializer."""
    brand         = BrandMinimalSerializer(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    cannabis_type = serializers.CharField(source="cannabis_profile.cannabis_type", read_only=True, default="")
    compliance_category = serializers.CharField(source="cannabis_profile.compliance_category", read_only=True, default="")

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
