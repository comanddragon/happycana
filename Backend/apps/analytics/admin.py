# =============================================================================
# apps/analytics/admin.py
# =============================================================================
from django.contrib import admin
from apps.analytics.models import Event, DailySalesSnapshot, ProductPerformance, ConversionFunnel


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "user", "session_key", "ip_address", "occurred_at"]
    list_filter = ["event_type", "occurred_at"]
    search_fields = ["user__email", "session_key"]
    readonly_fields = ["occurred_at"]
    raw_id_fields = ["user"]


@admin.register(DailySalesSnapshot)
class DailySalesSnapshotAdmin(admin.ModelAdmin):
    list_display = ["date", "total_orders", "total_revenue", "total_refunds", "net_revenue", "new_customers"]
    list_filter = ["date"]
    readonly_fields = [
        "date", "total_orders", "total_revenue",
        "total_refunds", "net_revenue", "new_customers",
        "items_sold", "created_at",
    ]

    def has_add_permission(self, request):
        return False  # computed by task only

    def has_delete_permission(self, request, obj=None):
        return False  # immutable audit records


@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ["product", "date", "views", "add_to_carts", "purchases", "revenue"]
    list_filter = ["date"]
    search_fields = ["product__name"]
    raw_id_fields = ["product"]
    readonly_fields = ["product", "date", "views", "add_to_carts", "purchases", "revenue"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConversionFunnel)
class ConversionFunnelAdmin(admin.ModelAdmin):
    list_display = ["date", "sessions", "product_views", "cart_adds", "checkout_starts", "purchases"]
    list_filter = ["date"]
    readonly_fields = [
        "date", "sessions", "product_views",
        "cart_adds", "checkout_starts", "purchases",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin

# Register your models here.
