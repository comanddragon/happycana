
# =============================================================================
# apps/payments/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.payments.models import Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Payment
        fields = ["id", "order", "gateway", "gateway_ref", "amount", "currency", "status", "created_at"]
        read_only_fields = ["id", "gateway_ref", "status", "created_at"]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Refund
        fields = ["id", "payment", "amount", "reason", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, data):
        payment = data["payment"]
        if payment.status != "success":
            raise serializers.ValidationError("Can only refund successfully completed payments.")
        existing_refunds = sum(r.amount for r in payment.refunds.filter(status="approved"))
        if data["amount"] + existing_refunds > payment.amount:
            raise serializers.ValidationError("Refund amount exceeds the original payment amount.")
        return data


class WebhookSerializer(serializers.Serializer):
    """Raw inbound payload from payment gateway webhooks (Stripe / PayPal)."""
    gateway    = serializers.CharField()
    event_type = serializers.CharField()
    payload    = serializers.JSONField()

