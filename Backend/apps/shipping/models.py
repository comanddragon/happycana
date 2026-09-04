import uuid
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db import models
from apps.orders.models import Order
from apps.inventory.models import Warehouse


class ShippingMethod(models.Model):
    """
    A reusable shipping option shown to customers at checkout
    (e.g. "DHL Express", "FedEx Ground").

    Admins manage these via the API; customers get a read-only list
    filtered to is_active=True.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="shipping_methods",
    )
    name = models.CharField(max_length=100)  # "DHL Express"
    carrier = models.CharField(max_length=50)  # "dhl" | "fedex"
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    estimated_days_min = models.PositiveSmallIntegerField()  # 1
    estimated_days_max = models.PositiveSmallIntegerField()  # 3
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "shipping_methods"
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.estimated_days_min}–{self.estimated_days_max} days, ${self.price})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.estimated_days_min > self.estimated_days_max:
            raise ValidationError(
                "estimated_days_min cannot be greater than estimated_days_max."
            )


class Shipment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PICKED = "picked", "Picked"
        SHIPPED = "shipped", "Shipped"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"

    # Valid forward transitions
    TRANSITIONS: dict[str, list[str]] = {
        Status.PENDING: [Status.PICKED, Status.RETURNED],
        Status.PICKED: [Status.SHIPPED, Status.RETURNED],
        Status.SHIPPED: [Status.IN_TRANSIT, Status.RETURNED],
        Status.IN_TRANSIT: [Status.DELIVERED, Status.RETURNED],
        Status.DELIVERED: [],
        Status.RETURNED: [],
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="shipments")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="shipments",
    )
    provider = models.CharField(max_length=50)  # "dhl" | "fedex"
    tracking_number = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "shipments"

    def __str__(self):
        return f"Shipment {self.tracking_number} — {self.status}"

    def transition_to(self, new_status: str) -> None:
        """
        Moves the shipment to new_status, auto-stamping timestamps,
        and raising ValueError for illegal transitions.
        """
        allowed = self.TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition shipment from '{self.status}' to '{new_status}'. "
                f"Allowed: {allowed or 'none'}"
            )
        self.status = new_status
        if new_status == self.Status.SHIPPED and not self.shipped_at:
            self.shipped_at = timezone.now()
        if new_status == self.Status.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        self.save(update_fields=["status", "shipped_at", "delivered_at"])


class TrackingEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="events"
    )
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "tracking_events"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.status} @ {self.location}"
