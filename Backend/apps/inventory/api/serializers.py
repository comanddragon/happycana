
# =============================================================================
# apps/inventory/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.inventory.models import Warehouse, Stock, StockMovement
from apps.catalog.api.serializers import ProductVariantSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Warehouse
        fields = ["id", "name", "address", "is_active"]
        read_only_fields = ["id"]


class StockSerializer(serializers.ModelSerializer):
    variant   = ProductVariantSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    available = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Stock
        fields = ["id", "variant", "warehouse", "quantity", "reserved", "available", "updated_at"]
        read_only_fields = ["id", "available", "updated_at"]


class StockWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Stock
        fields = ["variant", "warehouse", "quantity", "reserved"]

    def validate(self, data):
        reserved = data.get("reserved", 0)
        quantity = data.get("quantity", 0)
        if reserved > quantity:
            raise serializers.ValidationError("Reserved quantity cannot exceed total quantity.")
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StockMovement
        fields = ["id", "stock", "quantity_delta", "reason", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_quantity_delta(self, value):
        if value == 0:
            raise serializers.ValidationError("quantity_delta cannot be zero.")
        return value

