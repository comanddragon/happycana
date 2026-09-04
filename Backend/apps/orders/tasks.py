
# =============================================================================
# apps/orders/tasks.py
# =============================================================================
from django.tasks import task


@task()
def send_order_confirmation_email(order_id: str):
    from apps.orders.models import Order
    from services.email import EmailService
    try:
        order = Order.objects.select_related("user").prefetch_related("items__variant").get(id=order_id)
        EmailService.send_order_confirmation(order)
    except Order.DoesNotExist:
        pass


@task()
def auto_complete_delivered_orders():
    """
    Marks orders as DELIVERED if they've been in SHIPPED status
    for more than 14 days with no manual update.
    Run nightly via cron.
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.orders.models import Order
    from apps.shipping.models import Shipment

    cutoff = timezone.now() - timedelta(days=14)
    shipped_order_ids = (
        Shipment.objects
        .filter(status=Shipment.Status.SHIPPED, shipped_at__lt=cutoff)
        .values_list("order_id", flat=True)
    )
    Order.objects.ready_for_auto_complete(days=14).filter(
        id__in=shipped_order_ids
    ).update(status=Order.Status.DELIVERED)
