from django.db import models


class PeptideProfile(models.Model):
    product = models.OneToOneField(
        "catalog.Product", on_delete=models.CASCADE, related_name="peptide_profile"
    )
    sequence = models.CharField(max_length=500, blank=True)
    molecular_weight = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    purity_percent = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    form = models.CharField(max_length=100, blank=True)
    concentration = models.CharField(max_length=100, blank=True)
    storage_requirements = models.TextField(blank=True)
    documentation_url = models.URLField(blank=True)

    class Meta:
        db_table = "catalog_peptide_profiles"

    def __str__(self):
        return f"Peptide profile: {self.product}"
