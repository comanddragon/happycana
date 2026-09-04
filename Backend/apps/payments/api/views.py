# =============================================================================
# apps/payments/api/views.py
# =============================================================================
import hmac, hashlib
from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.payments.models import Payment, PaymentMethod, Refund
from apps.payments.gateways import GatewayFactory
from .serializers import PaymentMethodSerializer, PaymentSerializer, RefundSerializer, WebhookSerializer


class PaymentMethodListView(generics.ListAPIView):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PaymentListView(generics.ListAPIView):
    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Payment.objects.select_related("order").order_by("-created_at")


class PaymentDetailView(generics.RetrieveAPIView):
    queryset           = Payment.objects.select_related("order")
    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]


@method_decorator(ratelimit(key="user_or_ip", rate="20/m", method="POST", block=True), name="dispatch")
class InitiatePaymentView(APIView):
    """Creates a payment intent via the gateway and returns a client secret."""
    def post(self, request, order_pk):
        from apps.orders.models import Order
        gateway_name = request.data.get("gateway", "stripe")
        order   = Order.objects.get(pk=order_pk, user=request.user)
        gateway = GatewayFactory.get(gateway_name)
        result  = gateway.create_payment_intent(order)
        return Response({
            "gateway_ref":   result.gateway_ref,
            "client_secret": result.client_secret,
            "approval_url":  result.approval_url,
            "amount":        str(result.amount),
            "currency":      result.currency,
            "status":        result.status,
        }, status=status.HTTP_201_CREATED)


class RefundCreateView(generics.CreateAPIView):
    serializer_class   = RefundSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        refund = serializer.save()
        from apps.payments.tasks import process_refund
        process_refund.enqueue(refund_id=str(refund.id))


@method_decorator(ratelimit(key="ip", rate="60/m", method="POST", block=True), name="dispatch")
class StripeWebhookView(APIView):
    """Receives and verifies Stripe webhook events."""
    permission_classes     = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        payload    = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        gateway    = GatewayFactory.get("stripe")
        try:
            event = gateway.construct_webhook_event(payload, sig_header)
        except Exception:
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.payments.tasks import handle_stripe_event
        handle_stripe_event.enqueue(event_data=dict(event))
        return Response({"received": True})


@method_decorator(ratelimit(key="ip", rate="60/m", method="POST", block=True), name="dispatch")
class PayPalWebhookView(APIView):
    """Receives and verifies PayPal webhook events."""
    permission_classes     = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        gateway = GatewayFactory.get("paypal")
        try:
            event = gateway.handle_webhook(
                headers = request.META,
                body    = request.data,
            )
        except ValueError:
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.payments.tasks import handle_paypal_event
        handle_paypal_event.enqueue(event_data=event)
        return Response({"received": True})


@method_decorator(ratelimit(key="user_or_ip", rate="20/m", method="POST", block=True), name="dispatch")
class CapturePayPalPaymentView(APIView):
    """
    Called after the user returns from PayPal's approval URL.
    Captures the payment and confirms the order.
    """
    def post(self, request, order_pk):
        from apps.orders.models import Order
        from services.payment_services import PaymentService

        gateway_ref = request.data.get("gateway_ref")
        if not gateway_ref:
            return Response({"detail": "gateway_ref is required."}, status=status.HTTP_400_BAD_REQUEST)

        order   = Order.objects.get(pk=order_pk, user=request.user)
        gateway = GatewayFactory.get("paypal")
        try:
            result = gateway.capture(gateway_ref)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if result.status == "success":
            payment = PaymentService.confirm_payment(
                order       = order,
                gateway     = "paypal",
                gateway_ref = result.gateway_ref,
                amount      = result.amount,
                currency    = result.currency,
            )
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

        return Response({"detail": "Payment capture failed."}, status=status.HTTP_402_PAYMENT_REQUIRED)