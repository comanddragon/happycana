# =============================================================================
# apps/inventory/tasks.py
# =============================================================================
from django.tasks import task


@task()
def check_low_stock(stock_id: str, threshold: int = 5):
    """
    Re-evaluate a stock record after a movement.
    Creates an admin notification if stock falls below threshold.
    """
    from apps.inventory.models import Stock
    from apps.notifications.models import Notification
    from apps.users.models import User

    try:
        stock = Stock.objects.select_related("variant", "warehouse").get(id=stock_id)
    except Stock.DoesNotExist:
        return

    if stock.available <= threshold:
        admins = User.objects.filter(is_staff=True).values_list("id", flat=True)
        Notification.objects.bulk_create([
            Notification(
                user_id = admin_id,
                type    = Notification.Type.SYSTEM,
                title   = "Low Stock Alert",
                body    = (
                    f"SKU '{stock.variant.sku}' at {stock.warehouse.name} "
                    f"has only {stock.available} units remaining."
                ),
            )
            for admin_id in admins
        ])


@task()
def release_expired_reservations():
    """
    Periodically release stock reservations for orders stuck in PENDING
    for more than 30 minutes (e.g. abandoned checkouts).
    Run every 15 minutes via cron.
    """
    from apps.orders.models import Order
    from apps.inventory.models import Stock
    from django.db import models as db_models

    stale_orders = Order.objects.stale_pending(minutes=30).prefetch_related("items__variant")

    for order in stale_orders:
        for item in order.items.all():
            Stock.objects.filter(variant=item.variant).update(
                reserved=db_models.F("reserved") - item.quantity
            )
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
