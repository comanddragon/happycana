

# =============================================================================
# apps/analytics/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.analytics.models import Event, DailySalesSnapshot, ProductPerformance, ConversionFunnel


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Event
        fields = ["id", "event_type", "payload", "ip_address", "occurred_at"]
        read_only_fields = ["id", "ip_address", "occurred_at"]


class EventIngestSerializer(serializers.ModelSerializer):
    """
    Accepts inbound tracking events from the frontend.
    user and ip_address are set automatically in the view.
    """
    class Meta:
        model  = Event
        fields = ["event_type", "payload", "session_key"]

    def validate_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Payload must be a JSON object.")
        return value


class DailySalesSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DailySalesSnapshot
        fields = [
            "id", "date", "total_orders", "total_revenue",
            "total_refunds", "net_revenue", "new_customers",
            "items_sold", "created_at",
        ]
        read_only_fields = fields


class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model  = ProductPerformance
        fields = ["id", "product", "product_name", "date", "views", "add_to_carts", "purchases", "revenue"]
        read_only_fields = fields


class ConversionFunnelSerializer(serializers.ModelSerializer):
    view_to_cart_rate    = serializers.SerializerMethodField()
    cart_to_checkout_rate= serializers.SerializerMethodField()
    checkout_to_purchase_rate = serializers.SerializerMethodField()

    class Meta:
        model  = ConversionFunnel
        fields = [
            "id", "date", "sessions", "product_views", "cart_adds",
            "checkout_starts", "purchases",
            "view_to_cart_rate", "cart_to_checkout_rate", "checkout_to_purchase_rate",
        ]
        read_only_fields = fields

    def _rate(self, numerator, denominator):
        if not denominator:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    def get_view_to_cart_rate(self, obj):
        return self._rate(obj.cart_adds, obj.product_views)

    def get_cart_to_checkout_rate(self, obj):
        return self._rate(obj.checkout_starts, obj.cart_adds)

    def get_checkout_to_purchase_rate(self, obj):
        return self._rate(obj.purchases, obj.checkout_starts)
