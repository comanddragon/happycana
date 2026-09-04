# =============================================================================
# apps/shipping/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.shipping.models import Shipment, ShippingMethod, TrackingEvent


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ShippingMethod
        fields = [
            "id", "name", "carrier", "price",
            "estimated_days_min", "estimated_days_max", "is_active",
        ]
        read_only_fields = ["id"]

    def validate(self, data: dict) -> dict:
        min_days = data.get("estimated_days_min", getattr(self.instance, "estimated_days_min", None))
        max_days = data.get("estimated_days_max", getattr(self.instance, "estimated_days_max", None))
        if min_days is not None and max_days is not None and min_days > max_days:
            raise serializers.ValidationError(
                {"estimated_days_max": "estimated_days_max must be ≥ estimated_days_min."}
            )
        return data


class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TrackingEvent
        fields = ["id", "status", "location", "description", "occurred_at"]
        read_only_fields = ["id"]


class ShipmentSerializer(serializers.ModelSerializer):
    events          = TrackingEventSerializer(many=True, read_only=True)
    warehouse       = serializers.StringRelatedField(read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)

    class Meta:
        model  = Shipment
        fields = [
            "id", "order", "warehouse", "shipping_method", "provider",
            "tracking_number", "status",
            "shipped_at", "delivered_at", "events",
        ]
        read_only_fields = ["id", "shipped_at", "delivered_at"]


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    """
    Used by admins or provider webhooks to update shipment status.

    - `status`           — validated against allowed transitions; timestamps
                           are stamped automatically via Shipment.transition_to().
    - `tracking_number`  — freely updatable.
    - `shipping_method`  — writable by ID so admins can reassign the method.
    """

    class Meta:
        model  = Shipment
        fields = ["status", "tracking_number", "shipping_method"]

    def validate_status(self, new_status: str) -> str:
        allowed = Shipment.TRANSITIONS.get(self.instance.status, [])
        if new_status != self.instance.status and new_status not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from '{self.instance.status}' to '{new_status}'. "
                f"Allowed next statuses: {allowed or 'none'}."
            )
        return new_status

    def update(self, instance: Shipment, validated_data: dict) -> Shipment:
        new_status = validated_data.get("status")

        if new_status and new_status != instance.status:
            instance.transition_to(new_status)  # saves status + timestamps

        update_fields = []

        tracking_number = validated_data.get("tracking_number")
        if tracking_number is not None:
            instance.tracking_number = tracking_number
            update_fields.append("tracking_number")

        shipping_method = validated_data.get("shipping_method")
        if shipping_method is not None:
            instance.shipping_method = shipping_method
            update_fields.append("shipping_method")

        if update_fields:
            instance.save(update_fields=update_fields)

        return instance
