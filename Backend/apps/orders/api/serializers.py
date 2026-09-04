# =============================================================================
# apps/orders/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.catalog.api.serializers import ProductVariantSerializer
from apps.users.api.serializers import AddressSerializer
from apps.promotions.api.serializers import CouponSerializer


class CartItemSerializer(serializers.ModelSerializer):
    variant  = ProductVariantSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = CartItem
        fields = ["id", "variant", "quantity", "subtotal", "added_at"]
        read_only_fields = ["id", "added_at"]

    def get_subtotal(self, obj):
        return obj.variant.price * obj.quantity


class CartItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CartItem
        fields = ["variant", "quantity"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items       = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    item_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Cart
        fields = ["id", "items", "item_count", "total_price", "updated_at"]
        read_only_fields = ["id", "updated_at"]

    def get_total_price(self, obj):
        return sum(i.variant.price * i.quantity for i in obj.items.all())

    def get_item_count(self, obj):
        return obj.items.count()


class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model  = OrderItem
        fields = ["id", "variant", "quantity", "unit_price", "total_price"]
        read_only_fields = ["id"]


class OrderSerializer(serializers.ModelSerializer):
    items   = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    coupon  = CouponSerializer(read_only=True)
    payment_method = serializers.SerializerMethodField()

    def get_payment_method(self, obj):
        method = obj.payment_method
        return {
            "id": method.id,
            "name": method.name,
            "slug": method.slug,
            "description": method.description,
            "logo_url": method.logo_url,
        }

    class Meta:
        model  = Order
        fields = [
            "id", "status", "address", "coupon", "payment_method",
            "subtotal", "discount_amount", "shipping_cost", "total",
            "items", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "subtotal", "discount_amount", "total", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.Serializer):
    """
    Handed off to services/checkout.py which orchestrates the full
    cart → order → stock reservation → payment flow.
    """
    address_id = serializers.UUIDField()
    coupon_code= serializers.CharField(required=False, allow_blank=True)
    shipping_method_id = serializers.UUIDField()
    payment_method_id = serializers.IntegerField()

    def validate_address_id(self, value):
        user = self.context["request"].user
        if not user.addresses.filter(id=value).exists():
            raise serializers.ValidationError("Address not found.")
        return value

    def validate_shipping_method_id(self, value):
        from apps.shipping.models import ShippingMethod
        if not ShippingMethod.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Shipping method not found.")
        return value

    def validate_payment_method_id(self, value):
        from apps.payments.models import PaymentMethod
        if not PaymentMethod.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Payment method not found.")
        return value


class OrderStatusSerializer(serializers.ModelSerializer):
    """Admin-only serializer to manually update an order's status."""
    class Meta:
        model  = Order
        fields = ["status"]
