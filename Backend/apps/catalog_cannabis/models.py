from django.db import models


class CannabisProfile(models.Model):
    product = models.OneToOneField(
        "catalog.Product", on_delete=models.CASCADE, related_name="cannabis_profile"
    )
    product_type = models.CharField(max_length=50, blank=True)
    strain_type = models.CharField(max_length=50, blank=True)
    thc_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    cbd_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    terpenes = models.JSONField(default=dict, blank=True)
    effects = models.JSONField(default=list, blank=True)
    coa_url = models.URLField(blank=True)

    class Meta:
        db_table = "catalog_cannabis_profiles"

    def __str__(self):
        return f"Cannabis profile: {self.product}"
