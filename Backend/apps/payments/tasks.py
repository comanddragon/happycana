# =============================================================================
# apps/payments/tasks.py
# =============================================================================
from django.tasks import task


@task()
def process_refund(refund_id: str):
    from apps.payments.models import Refund
    from services.payment_services import PaymentService
    try:
        refund = Refund.objects.select_related("payment__order__user").get(id=refund_id)
        PaymentService.process_refund(refund)
    except Refund.DoesNotExist:
        pass


@task()
def handle_stripe_event(event_data: dict):
    """
    Processes inbound Stripe webhook events asynchronously.
    Dispatches to the relevant handler based on event type.
    """
    from apps.orders.models import Order
    from services.payment_services import PaymentService

    event_type = event_data.get("type")
    data_obj   = event_data.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        order_id = data_obj.get("metadata", {}).get("order_id")
        if not order_id:
            return
        try:
            order = Order.objects.get(id=order_id)
            PaymentService.confirm_payment(
                order       = order,
                gateway     = "stripe",
                gateway_ref = data_obj.get("id"),
                amount      = data_obj.get("amount_received", 0) / 100,
                currency    = data_obj.get("currency", "usd").upper(),
            )
        except Order.DoesNotExist:
            pass

    elif event_type == "payment_intent.payment_failed":
        order_id = data_obj.get("metadata", {}).get("order_id")
        if not order_id:
            return
        try:
            order = Order.objects.get(id=order_id)
            PaymentService.fail_payment(
                order       = order,
                gateway     = "stripe",
                gateway_ref = data_obj.get("id"),
                amount      = data_obj.get("amount", 0) / 100,
            )
        except Order.DoesNotExist:
            pass


@task()
def handle_paypal_event(event_data: dict):
    """
    Processes inbound PayPal webhook events asynchronously.
    PayPal uses different event type names from Stripe.
    """
    from apps.orders.models import Order
    from services.payment_services import PaymentService

    event_type = event_data.get("event_type")
    resource   = event_data.get("resource", {})

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        # Extract order_id from the custom_id field set during order creation
        order_id = resource.get("custom_id")
        if not order_id:
            return
        try:
            order = Order.objects.get(id=order_id)
            PaymentService.confirm_payment(
                order       = order,
                gateway     = "paypal",
                gateway_ref = resource.get("id"),
                amount      = resource.get("amount", {}).get("value", 0),
                currency    = resource.get("amount", {}).get("currency_code", "USD"),
            )
        except Order.DoesNotExist:
            pass

    elif event_type == "PAYMENT.CAPTURE.DENIED":
        order_id = resource.get("custom_id")
        if not order_id:
            return
        try:
            order = Order.objects.get(id=order_id)
            PaymentService.fail_payment(
                order       = order,
                gateway     = "paypal",
                gateway_ref = resource.get("id"),
                amount      = resource.get("amount", {}).get("value", 0),
            )
        except Order.DoesNotExist:
            pass
