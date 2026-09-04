import uuid

from django.db import models


class Storefront(models.Model):
    class Kind(models.TextChoices):
        GENERAL = "general", "General"
        DISPENSARY = "dispensary", "Dispensary"
        HASH = "hash", "Hash"
        PEPTIDES = "peptides", "Peptides"
        FOOTWEAR = "footwear", "Footwear"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.GENERAL)
    currency = models.CharField(max_length=3, default="USD")
    frontend_url = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    branding = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "storefronts"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StorefrontDomain(models.Model):
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "storefront_domains"

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower().rstrip(".")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain


class StorefrontOrigin(models.Model):
    storefront = models.ForeignKey(Storefront, on_delete=models.CASCADE, related_name="origins")
    origin = models.URLField(unique=True, help_text="Exact allowed browser origin, without a trailing slash.")

    class Meta:
        db_table = "storefront_origins"

    def save(self, *args, **kwargs):
        self.origin = self.origin.rstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.origin
