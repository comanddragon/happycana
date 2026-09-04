from django.db import models


class FootwearProfile(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", "New"
        LIKE_NEW = "like_new", "Like new"
        USED = "used", "Used"

    product = models.OneToOneField(
        "catalog.Product", on_delete=models.CASCADE, related_name="footwear_profile"
    )
    model_name = models.CharField(max_length=255, blank=True)
    style_code = models.CharField(max_length=100, blank=True)
    release_date = models.DateField(null=True, blank=True)
    size_system = models.CharField(max_length=20, blank=True)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW)
    authenticity_status = models.CharField(max_length=50, blank=True)
    box_condition = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "catalog_footwear_profiles"

    def __str__(self):
        return f"Footwear profile: {self.product}"
