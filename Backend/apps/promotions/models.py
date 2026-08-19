import uuid
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED      = "fixed",      "Fixed Amount"

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code           = models.CharField(max_length=50, unique=True)
    discount_type  = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses       = models.PositiveIntegerField(null=True, blank=True)
    used_count     = models.PositiveIntegerField(default=0)
    expires_at     = models.DateTimeField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = "coupons"

    def __str__(self):
        return self.code

