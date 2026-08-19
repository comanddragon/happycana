import uuid
from django.db import models
from apps.catalog.models import ProductVariant
from .managers import StockManager, StockMovementManager


class Warehouse(models.Model):
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name      = models.CharField(max_length=255)
    address   = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "warehouses"

    def __str__(self):
        return self.name


class Stock(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant    = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="stock_levels")
    warehouse  = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_levels")
    quantity   = models.PositiveIntegerField(default=0)
    reserved   = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    objects = StockManager()

    class Meta:
        db_table = "stock"
        unique_together = ("variant", "warehouse")

    @property
    def available(self):
        return self.quantity - self.reserved

    def __str__(self):
        return f"{self.variant.sku} @ {self.warehouse.name}: {self.available} available"


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        PURCHASE   = "purchase",   "Purchase"
        SALE       = "sale",       "Sale"
        RETURN     = "return",     "Return"
        ADJUSTMENT = "adjustment", "Adjustment"
        TRANSFER   = "transfer",   "Transfer"

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock          = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="movements")
    quantity_delta = models.IntegerField()  # positive = in, negative = out
    reason         = models.CharField(max_length=20, choices=Reason.choices)
    created_at     = models.DateTimeField(auto_now_add=True)
    objects = StockMovementManager()

    class Meta:
        db_table = "stock_movements"

    def __str__(self):
        return f"{self.quantity_delta:+d} on {self.stock} ({self.reason})"

