
# =============================================================================
# realtime/consumers/notifications.py
# =============================================================================
from channels.db import database_sync_to_async
from .base import BaseConsumer


class NotificationConsumer(BaseConsumer):
    """
    WebSocket: ws/notifications/
    - Each authenticated user gets their own private group channel.
    - New Notification model instances are pushed here by a signal.

    Client receives:
        { "type": "notification.new", "payload": { "id": "...", "title": "...", "body": "..." } }

    Client can send:
        { "action": "mark_read", "ids": ["uuid1", "uuid2"] }
    """

    async def connect(self):
        user = self.scope["user"]
        self.group_name = f"user_{user.id}_notifications"
        await self.join_group(self.group_name)
        await self.accept()
        unread = await self.get_unread_count(user)
        await self.send_json({"type": "connection.established", "payload": {"unread_count": unread}})

    async def disconnect(self, code):
        await self.leave_group(self.group_name)

    # ------------------------------------------------------------------
    # Incoming client messages
    # ------------------------------------------------------------------
    async def dispatch_action(self, action: str, content: dict):
        if action == "mark_read":
            ids = content.get("ids", [])
            await self.mark_read(ids)
            await self.send_json({"type": "notifications.marked_read", "payload": {"ids": ids}})
        else:
            await super().dispatch_action(action, content)

    # ------------------------------------------------------------------
    # Channel layer event handler
    # ------------------------------------------------------------------
    async def notification_new(self, event):
        await self.send_json({"type": "notification.new", "payload": event["payload"]})

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------
    @database_sync_to_async
    def get_unread_count(self, user):
        from apps.notifications.models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()

    @database_sync_to_async
    def mark_read(self, ids):
        from apps.notifications.models import Notification
        Notification.objects.filter(id__in=ids, user=self.scope["user"]).update(is_read=True)
