import uuid
from django.db import models
from apps.orders.models import Order
from .managers import PaymentManager, RefundManager


class PaymentMethod(models.Model):
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payment_methods",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    logo_url = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "payment_methods"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["storefront", "slug"],
                condition=models.Q(storefront__isnull=False),
                name="unique_storefront_payment_slug",
            ),
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(storefront__isnull=True),
                name="unique_legacy_payment_slug",
            ),
        ]

    def __str__(self):
        return self.name


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    gateway = models.CharField(max_length=50)  # "stripe" | "paypal"
    gateway_ref = models.CharField(max_length=255)  # external transaction ID
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = PaymentManager()

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment {self.gateway_ref} — {self.status}"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment, on_delete=models.PROTECT, related_name="refunds"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = RefundManager()

    class Meta:
        db_table = "refunds"

    def __str__(self):
        return f"Refund {self.id} — {self.status}"
