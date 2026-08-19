
# =============================================================================
# realtime/consumers/order_status.py
# =============================================================================
from channels.db import database_sync_to_async
from .base import BaseConsumer


class OrderStatusConsumer(BaseConsumer):
    """
    WebSocket: ws/orders/<order_id>/
    - Authenticated user connects to track their order in real time.
    - Broadcasts status changes pushed by the orders app signal.

    Client receives:
        { "type": "order.status_changed", "payload": { "order_id": "...", "status": "shipped" } }
    """

    async def connect(self):
        self.order_id  = self.scope["url_route"]["kwargs"]["order_id"]
        self.group_name = f"order_{self.order_id}"
        user = self.scope["user"]

        # Verify the user owns this order
        if not await self.user_owns_order(user, self.order_id):
            await self.close(code=4003)
            return

        await self.join_group(self.group_name)
        await self.accept()
        await self.send_json({"type": "connection.established", "payload": {"order_id": self.order_id}})

    async def disconnect(self, code):
        await self.leave_group(self.group_name)

    # ------------------------------------------------------------------
    # Channel layer event handler — called when group_send is triggered
    # ------------------------------------------------------------------
    async def order_status_changed(self, event):
        await self.send_json({"type": "order.status_changed", "payload": event["payload"]})

    # ------------------------------------------------------------------
    # DB helper
    # ------------------------------------------------------------------
    @database_sync_to_async
    def user_owns_order(self, user, order_id):
        from apps.orders.models import Order
        if user.is_staff:
            return True
        return Order.objects.filter(id=order_id, user=user).exists()
