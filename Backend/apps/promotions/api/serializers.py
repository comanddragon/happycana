
# =============================================================================
# apps/promotions/api/serializers.py
# =============================================================================
from django.utils import timezone
from rest_framework import serializers
from apps.promotions.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model  = Coupon
        fields = [
            "id", "code", "discount_type", "discount_value",
            "min_order_value", "max_uses", "used_count",
            "expires_at", "is_active", "is_expired",
        ]
        read_only_fields = ["id", "used_count", "is_expired"]

    def get_is_expired(self, obj):
        if obj.expires_at and obj.expires_at < timezone.now():
            return True
        if obj.max_uses and obj.used_count >= obj.max_uses:
            return True
        return False


class CouponValidateSerializer(serializers.Serializer):
    """Used by the checkout flow to validate and apply a coupon code."""
    code        = serializers.CharField()
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, data):
        try:
            coupon = Coupon.objects.get(code=data["code"], is_active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid or inactive coupon code."})

        if coupon.expires_at and coupon.expires_at < timezone.now():
            raise serializers.ValidationError({"code": "This coupon has expired."})

        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            raise serializers.ValidationError({"code": "This coupon has reached its usage limit."})

        if data["order_total"] < coupon.min_order_value:
            raise serializers.ValidationError({
                "code": f"Minimum order value for this coupon is {coupon.min_order_value}."
            })

        data["coupon"] = coupon
        return data

