
# =============================================================================
# apps/inventory/admin.py
# =============================================================================
from django.contrib import admin
from apps.inventory.models import Warehouse, Stock, StockMovement


class StockMovementInline(admin.TabularInline):
    model          = StockMovement
    extra          = 0
    readonly_fields= ["quantity_delta", "reason", "created_at"]
    can_delete     = False


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display  = ["name", "address", "is_active"]
    list_filter   = ["is_active"]
    search_fields = ["name"]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    inlines        = [StockMovementInline]
    list_display   = ["variant", "warehouse", "quantity", "reserved", "available_display", "updated_at"]
    list_filter    = ["warehouse"]
    search_fields  = ["variant__sku"]
    readonly_fields= ["updated_at"]
    raw_id_fields  = ["variant", "warehouse"]

    @admin.display(description="Available")
    def available_display(self, obj):
        return obj.available


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display   = ["stock", "quantity_delta", "reason", "created_at"]
    list_filter    = ["reason", "created_at"]
    readonly_fields= ["created_at"]
    raw_id_fields  = ["stock"]
