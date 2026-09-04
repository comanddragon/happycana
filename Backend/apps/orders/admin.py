
# =============================================================================
# apps/orders/admin.py
# =============================================================================
from django.contrib import admin
from apps.orders.models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model  = CartItem
    extra  = 0
    fields = ["variant", "quantity", "added_at"]
    readonly_fields = ["added_at"]


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ["unit_price", "total_price"]
    raw_id_fields   = ["variant"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines      = [CartItemInline]
    list_display = ["user", "session_key", "updated_at"]
    raw_id_fields= ["user"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines         = [OrderItemInline]
    list_display    = ["id", "user", "payment_method", "status", "total", "created_at"]
    list_filter     = ["payment_method", "status", "created_at"]
    search_fields   = ["user__email", "id"]
    readonly_fields = ["subtotal", "discount_amount", "shipping_cost", "total", "created_at", "updated_at"]
    raw_id_fields   = ["user", "address", "coupon"]

    # Admins can update the order status directly from the change view
    fieldsets = (
        ("Order Info",  {"fields": ("user", "address", "coupon", "payment_method", "status")}),
        ("Financials",  {"fields": ("subtotal", "discount_amount", "shipping_cost", "total")}),
        ("Timestamps",  {"fields": ("created_at", "updated_at")}),
    )

    actions = ["mark_confirmed", "mark_processing", "mark_shipped", "mark_cancelled"]

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status=Order.Status.PROCESSING)

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Order.Status.CANCELLED)
