

# =============================================================================
# apps/shipping/admin.py
# =============================================================================
from django.contrib import admin
from apps.shipping.models import Shipment, TrackingEvent, ShippingMethod


class TrackingEventInline(admin.TabularInline):
    model           = TrackingEvent
    extra           = 0
    readonly_fields = ["status", "location", "description", "occurred_at"]
    can_delete      = False


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    inlines         = [TrackingEventInline]
    list_display    = ["id", "order", "provider", "tracking_number", "status", "shipped_at"]
    list_filter     = ["provider", "status", "shipped_at"]
    search_fields   = ["tracking_number", "order__id"]
    readonly_fields = ["shipped_at", "delivered_at"]
    raw_id_fields   = ["order", "warehouse"]

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display    = ["name", "carrier", "price", "estimated_days_min", "estimated_days_max"]
    list_filter     = ["name", "carrier"]
    search_fields   = ["name", "carrier"]

@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display  = ["shipment", "status", "location", "occurred_at"]
    list_filter   = ["occurred_at"]
    raw_id_fields = ["shipment"]
