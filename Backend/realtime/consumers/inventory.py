
# =============================================================================
# realtime/consumers/inventory.py
# =============================================================================
from .base import BaseConsumer


class InventoryConsumer(BaseConsumer):
    """
    WebSocket: ws/inventory/
    - Admin-only feed of live stock level changes.
    - Broadcasts whenever a StockMovement is saved (via signal).

    Client receives:
        { "type": "inventory.stock_updated", "payload": { "sku": "...", "available": 12 } }
    Client receives:
        { "type": "inventory.low_stock", "payload": { "sku": "...", "available": 2, "threshold": 5 } }
    """
    GROUP_NAME = "inventory_updates"

    async def connect(self):
        if not self.scope["user"].is_staff:
            await self.close(code=4003)
            return
        await self.join_group(self.GROUP_NAME)
        await self.accept()
        await self.send_json({"type": "connection.established", "payload": {"room": "inventory"}})

    async def disconnect(self, code):
        await self.leave_group(self.GROUP_NAME)

    # ------------------------------------------------------------------
    # Channel layer event handlers
    # ------------------------------------------------------------------
    async def inventory_stock_updated(self, event):
        await self.send_json({"type": "inventory.stock_updated", "payload": event["payload"]})

    async def inventory_low_stock(self, event):
        await self.send_json({"type": "inventory.low_stock", "payload": event["payload"]})
