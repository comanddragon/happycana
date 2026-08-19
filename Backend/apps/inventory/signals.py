
# =============================================================================
# apps/inventory/signals.py  — Fires stock update + low-stock WS broadcast
# =============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.inventory.models import StockMovement

LOW_STOCK_THRESHOLD = 5


@receiver(post_save, sender=StockMovement)
def broadcast_stock_update(sender, instance, created, **kwargs):
    if not created:
        return
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    stock         = instance.stock
    channel_layer = get_channel_layer()

    # Always broadcast updated stock level
    async_to_sync(channel_layer.group_send)(
        "inventory_updates",
        {
            "type":    "inventory_stock_updated",
            "payload": {
                "sku":       stock.variant.sku,
                "quantity":  stock.quantity,
                "reserved":  stock.reserved,
                "available": stock.available,
                "warehouse": stock.warehouse.name,
            },
        }
    )

    # Additionally broadcast a low-stock alert if threshold is breached
    if stock.available <= LOW_STOCK_THRESHOLD:
        async_to_sync(channel_layer.group_send)(
            "inventory_updates",
            {
                "type":    "inventory_low_stock",
                "payload": {
                    "sku":       stock.variant.sku,
                    "available": stock.available,
                    "threshold": LOW_STOCK_THRESHOLD,
                    "warehouse": stock.warehouse.name,
                },
            }
        )
