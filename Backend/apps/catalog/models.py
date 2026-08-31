import uuid
from django.db import models
from .managers import CategoryManager, ProductManager, ProductVariantManager


# ─── Mixins ───────────────────────────────────────────────────────────────────

class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MediaMixin(models.Model):
    """Shared fields and logic for image/video attachments."""
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def _enforce_single_primary(self, qs):
        """Unset is_primary on all siblings before saving this one as primary."""
        if self.is_primary:
            qs.exclude(pk=self.pk).update(is_primary=False)


class VideoMixin(models.Model):
    class VideoType(models.TextChoices):
        UPLOAD  = "upload",  "Direct Upload"
        YOUTUBE = "youtube", "YouTube"
        VIMEO   = "vimeo",   "Vimeo"

    video_type   = models.CharField(max_length=20, choices=VideoType.choices, default=VideoType.UPLOAD)
    file         = models.FileField(blank=True, null=True)
    external_url = models.URLField(blank=True)
    thumbnail    = models.ImageField(blank=True, null=True)
    title        = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    @property
    def url(self):
        if self.video_type == self.VideoType.UPLOAD and self.file:
            return self.file.url
        return self.external_url

class Brand(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=255, unique=True)
    slug        = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    logo_url    = models.URLField(blank=True, help_text="Passed through as-is from the source — not downloaded/re-hosted.")
    website     = models.URLField(blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "id"]
        db_table = "brands"

    def __str__(self):
        return self.name

class Effect(models.Model):
    """
    NEW MODEL. e.g. "relaxed", "energized", "creative". Backed by a real
    table (not free-text) so it's cheaply filterable/facetable.
    """
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name", "id"]
        db_table = "effects"

    def __str__(self):
        return self.name

# ─── Catalog ──────────────────────────────────────────────────────────────────

class Category(UUIDModel):
    parent      = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to="categories/images/", blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    objects = CategoryManager()

    class Meta:
        ordering = ["name", "id"]
        db_table            = "categories"
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if self.image and self.image.name.startswith(("http://", "https://")):
            raise ValueError(
                f"Category.image must be an uploaded file, not a URL: {self.image.name!r}. "
                "Download the image and assign it via ContentFile, e.g. "
                "category.image.save(filename, ContentFile(response.content))."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(TimestampedModel):
    category         = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name             = models.CharField(max_length=255)
    slug             = models.SlugField(max_length=255, unique=True)
    description      = models.TextField(blank=True)
    base_price       = models.DecimalField(max_digits=12, decimal_places=2)
    is_active        = models.BooleanField(default=True)
    meta_title       = models.CharField(max_length=60, blank=True)   # fallback to name if empty
    meta_description = models.CharField(max_length=160, blank=True)  # fallback to description[:160]
    class ComplianceCategory(models.TextChoices):
        FLOWER        = "flower",        "Flower"
        VAPORIZERS    = "vaporizers",    "Vaporizers"
        EDIBLES       = "edibles",       "Edibles"
        CONCENTRATES  = "concentrates",  "Concentrates"
        PRE_ROLLS     = "pre_rolls",     "Pre-Rolls"
        TINCTURES     = "tinctures",     "Tinctures"
        TOPICALS      = "topicals",      "Topicals"
        BEVERAGES     = "beverages",     "Beverages"
        ACCESSORIES   = "accessories",   "Accessories"
        MERCHANDISE   = "merchandise",   "Merchandise"
        CBD_PRODUCTS  = "cbd_products",  "CBD Products"
        GIFT_CARDS    = "gift_cards",    "Gift Cards"

    class CannabisType(models.TextChoices):
        SATIVA        = "sativa",         "Sativa"
        INDICA        = "indica",         "Indica"
        HYBRID        = "hybrid",         "Hybrid"
        HYBRID_SATIVA = "hybrid_sativa",  "Hybrid (Sativa Leaning)"
        HYBRID_INDICA = "hybrid_indica",  "Hybrid (Indica Leaning)"
        NA            = "na",             "N/A"

    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    compliance_category = models.CharField(
        max_length=20, choices=ComplianceCategory.choices, blank=True,
        help_text="Regulatory product type — distinct from the display Category.",
    )
    cannabis_type = models.CharField(
        max_length=20, choices=CannabisType.choices, blank=True,
    )
    sub_type = models.CharField(max_length=100, blank=True)
    effects = models.ManyToManyField(Effect, blank=True, related_name="products")

    is_featured = models.BooleanField(default=False)
    is_new      = models.BooleanField(default=False)

    external_source_id = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        help_text="POS / scrape source ID — used to upsert on re-import instead of duplicating.",
    )
    units_sold_hint = models.PositiveIntegerField(
        default=0, help_text="Informational popularity signal from source data, not order history.",
    )

    objects = ProductManager()

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first()

    @property
    def primary_video(self):
        return self.videos.filter(is_primary=True).first()


# ─── Product media ────────────────────────────────────────────────────────────
class ProductImage(UUIDModel, MediaMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image   = models.ImageField(upload_to="products/images/", blank=True, null=True)
    source_url = models.URLField(
        blank=True, help_text="Passed through as-is from the source — not downloaded/re-hosted."
    )
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "product_images"
        ordering = ["order", "created_at"]

    def save(self, *args, **kwargs):
        if not self.alt_text and self.product_id:
            self.alt_text = self.product.name   # sensible default, still editable in admin
        self._enforce_single_primary(
            ProductImage.objects.filter(product=self.product, is_primary=True)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = "primary" if self.is_primary else f"#{self.order}"
        return f"Image for {self.product.name} ({suffix})"


class ProductVideo(UUIDModel, MediaMixin, VideoMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="videos")
    file    = models.FileField(upload_to="products/videos/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="products/video_thumbnails/", blank=True, null=True)

    class Meta:
        db_table = "product_videos"
        ordering = ["order", "created_at"]

    def save(self, *args, **kwargs):
        self._enforce_single_primary(
            ProductVideo.objects.filter(product=self.product, is_primary=True)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = "primary" if self.is_primary else f"#{self.order}"
        return f"Video for {self.product.name} ({suffix})"


# ─── Variants ─────────────────────────────────────────────────────────────────

class ProductVariant(UUIDModel):
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku       = models.CharField(max_length=100, unique=True)
    price     = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class WeightUnit(models.TextChoices):
        GRAMS      = "grams",      "Grams"
        MILLIGRAMS = "milligrams", "Milligrams"
        EACH       = "each",       "Each"
        UNKNOWN    = "unknown",    "Unknown"

    weight_value = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    weight_unit  = models.CharField(max_length=12, choices=WeightUnit.choices, blank=True)

    objects = ProductVariantManager()

    class Meta:
        db_table = "product_variants"

    def __str__(self):
        return self.sku


# ─── Variant media ────────────────────────────────────────────────────────────

class VariantImage(UUIDModel, MediaMixin):
    variant  = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images")
    image    = models.ImageField(upload_to="products/variants/images/")
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "variant_images"
        ordering = ["order", "created_at"]

    def save(self, *args, **kwargs):
        self._enforce_single_primary(
            VariantImage.objects.filter(variant=self.variant, is_primary=True)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = "primary" if self.is_primary else f"#{self.order}"
        return f"Image for {self.variant.sku} ({suffix})"


class VariantVideo(UUIDModel, MediaMixin, VideoMixin):
    variant   = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="videos")
    file      = models.FileField(upload_to="products/variants/videos/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="products/variants/video_thumbnails/", blank=True, null=True)

    class Meta:
        db_table = "variant_videos"
        ordering = ["order", "created_at"]

    def save(self, *args, **kwargs):
        self._enforce_single_primary(
            VariantVideo.objects.filter(variant=self.variant, is_primary=True)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        suffix = "primary" if self.is_primary else f"#{self.order}"
        return f"Video for {self.variant.sku} ({suffix})"


# ─── Attributes ───────────────────────────────────────────────────────────────

class AttributeType(UUIDModel):
    """Reusable attribute definition, e.g. 'Color', 'Size'."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "attribute_types"

    def __str__(self):
        return self.name


class Attribute(UUIDModel):
    """A concrete attribute value attached to a variant, e.g. Color=Red."""
    variant        = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="attributes", null=True, blank=True)
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.PROTECT, related_name="values", null=True, blank=True)
    value          = models.CharField(max_length=100)

    class Meta:
        db_table        = "attributes"
        unique_together = [("variant", "attribute_type")]

    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"


# ─── Lab results / COA ────────────────────────────────────────────────────────

class Lab(models.Model):
    """
    NEW MODEL, one-to-one with ProductVariant. Kept off the hot Product/
    Variant list-query path deliberately — 20+ nullable decimal columns
    don't belong on every catalog list response, only product-detail.
    """
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.OneToOneField(
        "ProductVariant", on_delete=models.CASCADE, related_name="lab"
    )

    class Potency(models.TextChoices):
        MILD   = "mild",   "Mild"
        MEDIUM = "medium", "Medium"
        STRONG = "strong", "Strong"

    potency = models.CharField(max_length=10, choices=Potency.choices, blank=True)

    thc_percent  = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    thca_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbd_percent  = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbda_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbn_percent  = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbg_percent  = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)

    # Terpene profile — stored as JSON {name: mg_value} rather than one
    # column per terpene (12+ distinct terpenes appear across the catalog,
    # rarely more than 6-9 on any single product).
    terpenes = models.JSONField(default=dict, blank=True)

    coa_url  = models.URLField(blank=True, help_text="Link to third-party Certificate of Analysis, if hosted externally.")
    coa_file = models.FileField(upload_to="lab_reports/", blank=True, null=True)

    class Meta:
        db_table = "product_labs"

    def __str__(self):
        return f"Lab results for {self.variant.sku}"


# ─── ProductDiscount (phase 2 — not required by the seed script) ─────────────

class ProductDiscount(models.Model):
    """
    NEW MODEL. Distinct from apps.promotions.Coupon: this is an automatic,
    schedule-aware, per-product discount (no code entry). 469/1689 scraped
    products carry one of these. Seed script currently skips populating
    this — base prices are seeded as-is — flagged here as a phase 2 item.
    """
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="discounts")

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED   = "fixed",   "Fixed Amount"

    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value         = models.DecimalField(max_digits=8, decimal_places=2)
    starts_at     = models.DateTimeField(null=True, blank=True)
    ends_at       = models.DateTimeField(null=True, blank=True)
    days_of_week  = models.JSONField(default=list, blank=True, help_text="0=Sun..6=Sat, empty=every day")
    is_stackable  = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=True)

    class Meta:
        db_table = "product_discounts"

    def __str__(self):
        return f"{self.product.name}: {self.value}{'%' if self.discount_type == 'percent' else ''} off"
