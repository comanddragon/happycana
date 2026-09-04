import uuid
from django.db import models
from apps.users.models import User, Address
from apps.catalog.models import ProductVariant
from apps.promotions.models import Coupon
from .managers import CartManager, OrderManager


class Cart(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    session_key = models.CharField(max_length=100, blank=True)  # for anonymous carts
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    objects = CartManager()

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart({self.user or self.session_key})"


class CartItem(models.Model):
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant  = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table       = "cart_items"
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.quantity}x {self.variant.sku}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        CONFIRMED  = "confirmed",  "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED    = "shipped",    "Shipped"
        DELIVERED  = "delivered",  "Delivered"
        CANCELLED  = "cancelled",  "Cancelled"
        REFUNDED   = "refunded",   "Refunded"

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    address         = models.ForeignKey(Address, on_delete=models.PROTECT)
    shipping_method = models.ForeignKey("shipping.ShippingMethod", on_delete=models.PROTECT, null=True, blank=True)
    payment_method  = models.ForeignKey("payments.PaymentMethod", on_delete=models.PROTECT, related_name="orders")
    coupon          = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=12, decimal_places=2)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    objects = OrderManager()

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} — {self.status}"

    @property
    def short_id(self):
        return str(self.id)[:8].upper()


class OrderItem(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant     = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity    = models.PositiveIntegerField()
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.quantity}x {self.variant.sku} on Order {self.order_id}"
