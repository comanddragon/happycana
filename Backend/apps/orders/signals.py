
# =============================================================================
# apps/orders/signals.py  — Fires the order status WS broadcast
# =============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order


@receiver(post_save, sender=Order)
def broadcast_order_status(sender, instance, created, **kwargs):
    if created:
        return
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"order_{instance.id}",
        {
            "type":    "order_status_changed",
            "payload": {
                "order_id": str(instance.id),
                "status":   instance.status,
            },
        }
    )