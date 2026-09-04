# =============================================================================
# apps/analytics/models.py
# =============================================================================
import uuid
from django.db import models
from apps.users.models import User
from apps.catalog.models import Product
from .managers import EventManager, DailySalesSnapshotManager, ProductPerformanceManager


class Event(models.Model):
    """Generic user behaviour event (page view, click, search, etc.)"""

    class EventType(models.TextChoices):
        PAGE_VIEW = "page_view", "Page View"
        PRODUCT_VIEW = "product_view", "Product View"
        ADD_TO_CART = "add_to_cart", "Add to Cart"
        REMOVE_FROM_CART = "remove_from_cart", "Remove from Cart"
        SEARCH = "search", "Search"
        CHECKOUT_START = "checkout_start", "Checkout Start"
        PURCHASE = "purchase", "Purchase"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    session_key = models.CharField(max_length=100, blank=True)  # for anonymous users
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    payload = models.JSONField(
        default=dict, blank=True
    )  # flexible extra data per event type
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    objects = EventManager()

    class Meta:
        db_table = "analytics_events"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["event_type", "occurred_at"]),
            models.Index(fields=["user", "occurred_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} @ {self.occurred_at}"


class DailySalesSnapshot(models.Model):
    """
    Pre-aggregated daily sales figures computed by a nightly task.
    Avoids expensive live aggregations on large orders tables.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="daily_sales_snapshots",
    )
    date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_refunds = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    new_customers = models.PositiveIntegerField(default=0)
    items_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = DailySalesSnapshotManager()

    class Meta:
        db_table = "analytics_daily_sales"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["storefront", "date"],
                condition=models.Q(storefront__isnull=False),
                name="unique_storefront_daily_sales",
            ),
            models.UniqueConstraint(
                fields=["date"],
                condition=models.Q(storefront__isnull=True),
                name="unique_legacy_daily_sales",
            ),
        ]

    def __str__(self):
        return f"Sales snapshot {self.date} — ${self.net_revenue}"


class ProductPerformance(models.Model):
    """
    Per-product daily stats: views, add-to-carts, purchases.
    Rolled up nightly so dashboards stay fast.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product_performance",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="performance"
    )
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    add_to_carts = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    objects = ProductPerformanceManager()

    class Meta:
        db_table = "analytics_product_performance"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["storefront", "product", "date"],
                condition=models.Q(storefront__isnull=False),
                name="unique_storefront_product_performance",
            ),
            models.UniqueConstraint(
                fields=["product", "date"],
                condition=models.Q(storefront__isnull=True),
                name="unique_legacy_product_performance",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} on {self.date}"


class ConversionFunnel(models.Model):
    """
    Tracks how many sessions progress through each checkout stage daily.
    Used to identify where users drop off.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storefront = models.ForeignKey(
        "storefronts.Storefront",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="conversion_funnels",
    )
    date = models.DateField()
    sessions = models.PositiveIntegerField(default=0)
    product_views = models.PositiveIntegerField(default=0)
    cart_adds = models.PositiveIntegerField(default=0)
    checkout_starts = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "analytics_conversion_funnel"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["storefront", "date"],
                condition=models.Q(storefront__isnull=False),
                name="unique_storefront_conversion_funnel",
            ),
            models.UniqueConstraint(
                fields=["date"],
                condition=models.Q(storefront__isnull=True),
                name="unique_legacy_conversion_funnel",
            ),
        ]

    def __str__(self):
        return (
            f"Funnel {self.date}: {self.sessions} sessions → {self.purchases} purchases"
        )
