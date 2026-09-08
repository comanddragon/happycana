

# =============================================================================
# apps/shipping/admin.py
# =============================================================================
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.shipping.models import Shipment, ShippingMethod, TrackingEvent


class TrackingEventInline(TabularInline):
    model           = TrackingEvent
    extra           = 0
    readonly_fields = ["status", "location", "description", "occurred_at"]
    can_delete      = False


@admin.register(Shipment)
class ShipmentAdmin(ModelAdmin):
    inlines         = [TrackingEventInline]
    list_display    = ["id", "order", "provider", "tracking_number", "status", "shipped_at"]
    list_filter     = ["provider", "status", "shipped_at"]
    search_fields   = ["tracking_number", "order__id"]
    readonly_fields = ["shipped_at", "delivered_at"]
    raw_id_fields   = ["order", "warehouse"]

@admin.register(ShippingMethod)
class ShippingMethodAdmin(ModelAdmin):
    list_display    = ["name", "carrier", "is_global", "price", "estimated_days_min", "estimated_days_max"]
    list_filter     = ["is_global", "storefronts", "carrier", "is_active"]
    filter_horizontal = ["storefronts"]
    search_fields   = ["name", "carrier"]

@admin.register(TrackingEvent)
class TrackingEventAdmin(ModelAdmin):
    list_display  = ["shipment", "status", "location", "occurred_at"]
    list_filter   = ["occurred_at"]
    raw_id_fields = ["shipment"]
