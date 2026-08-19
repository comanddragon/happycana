
# =============================================================================
# realtime/consumers/base.py
# =============================================================================
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
import logging


class BaseConsumer(AsyncJsonWebsocketConsumer):
    """
    Shared base for all consumers.
    - Rejects unauthenticated connections unless allow_anonymous = True
    - Provides helpers: push(), join_group(), leave_group()
    """
    allow_anonymous = False

    async def websocket_connect(self, message):
        if not self.allow_anonymous and isinstance(self.scope["user"], AnonymousUser):
            logging.getLogger(__name__).warning(
                "WebSocket rejected — unauthenticated connection from %s",
                self.scope.get("client"),
            )
            await self.close(code=4001)
            return
        logging.getLogger(__name__).info(
            "WebSocket handshake — user=%s path=%s",
            getattr(self.scope["user"], "email", "anonymous"),
            self.scope.get("path"),
        )
        await super().websocket_connect(message)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def join_group(self, group_name: str):
        await self.channel_layer.group_add(group_name, self.channel_name)

    async def leave_group(self, group_name: str):
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def push(self, group_name: str, event_type: str, payload: dict):
        """Broadcast a message to an entire channel group."""
        await self.channel_layer.group_send(group_name, {
            "type":    event_type,   # maps to a handler method on the consumer
            "payload": payload,
        })

    # ------------------------------------------------------------------
    # Default error handler
    # ------------------------------------------------------------------
    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if not action:
            await self.send_json({"error": "Missing 'action' field."})
            return
        await self.dispatch_action(action, content)

    async def dispatch_action(self, action: str, content: dict):
        """Override in subclasses to handle incoming client messages."""
        await self.send_json({"error": f"Unknown action: {action}"})
