from django.db import models


class CannabisProfile(models.Model):
    class ComplianceCategory(models.TextChoices):
        FLOWER = "flower", "Flower"
        VAPORIZERS = "vaporizers", "Vaporizers"
        EDIBLES = "edibles", "Edibles"
        CONCENTRATES = "concentrates", "Concentrates"
        PRE_ROLLS = "pre_rolls", "Pre-Rolls"
        TINCTURES = "tinctures", "Tinctures"
        TOPICALS = "topicals", "Topicals"
        BEVERAGES = "beverages", "Beverages"
        ACCESSORIES = "accessories", "Accessories"
        MERCHANDISE = "merchandise", "Merchandise"
        CBD_PRODUCTS = "cbd_products", "CBD Products"
        GIFT_CARDS = "gift_cards", "Gift Cards"

    class CannabisType(models.TextChoices):
        SATIVA = "sativa", "Sativa"
        INDICA = "indica", "Indica"
        HYBRID = "hybrid", "Hybrid"
        HYBRID_SATIVA = "hybrid_sativa", "Hybrid (Sativa Leaning)"
        HYBRID_INDICA = "hybrid_indica", "Hybrid (Indica Leaning)"
        NA = "na", "N/A"

    product = models.OneToOneField(
        "catalog.Product", on_delete=models.CASCADE, related_name="cannabis_profile"
    )
    compliance_category = models.CharField(
        max_length=20, choices=ComplianceCategory.choices, blank=True
    )
    cannabis_type = models.CharField(max_length=20, choices=CannabisType.choices, blank=True)
    sub_type = models.CharField(max_length=100, blank=True)
    thc_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbd_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    terpenes = models.JSONField(default=dict, blank=True)
    effects_legacy = models.JSONField(default=list, blank=True)
    effect_tags = models.ManyToManyField("catalog.Effect", blank=True, related_name="cannabis_profiles")
    coa_url = models.URLField(blank=True)

    class Meta:
        db_table = "catalog_cannabis_profiles"

    def __str__(self):
        return f"Cannabis profile: {self.product}"
