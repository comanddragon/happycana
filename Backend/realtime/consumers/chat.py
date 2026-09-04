# =============================================================================
# realtime/consumers/chat.py   (replaces the stub version)
# =============================================================================
from channels.db import database_sync_to_async
from django.utils import timezone
from .base import BaseConsumer


class ChatConsumer(BaseConsumer):
    """
    WebSocket: ws/chat/<room_id>/
    Full-featured customer-support chat consumer.

    Client → server actions
    -----------------------
    { "action": "send_message", "body": "Where is my order?", "message_type": "text" }
    { "action": "typing",       "is_typing": true }
    { "action": "read_messages" }   — marks all unread messages as read

    Server → client events
    ----------------------
    { "type": "chat.message",  "payload": { id, sender_email, sender_name,
                                             message_type, body, created_at, is_own } }
    { "type": "chat.typing",   "payload": { "sender": "email", "is_typing": true } }
    { "type": "chat.join",     "payload": { "sender": "email" } }
    { "type": "chat.leave",    "payload": { "sender": "email" } }
    { "type": "chat.read",     "payload": { "reader": "email" } }
    { "type": "chat.history",  "payload": { "messages": [...] } }   — sent on connect
    """

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        user = self.scope["user"]

        # Verify the user is a participant (customer, agent, or staff)
        if not await self.can_access_room(user, self.room_id):
            await self.close(code=4003)
            return

        self.group_name = await self.get_group_name(self.room_id)

        await self.join_group(self.group_name)
        await self.accept()

        # Send message history on connect so client has context
        history = await self.get_message_history(self.room_id, user)
        await self.send_json({"type": "chat.history", "payload": {"messages": history}})

        # Announce join to everyone else
        await self.push(
            self.group_name,
            "chat_join",
            {
                "sender": user.email,
            },
        )

    async def disconnect(self, code):
        user = self.scope["user"]
        await self.push(
            self.group_name,
            "chat_leave",
            {
                "sender": getattr(user, "email", "anonymous"),
            },
        )
        await self.leave_group(self.group_name)

    # ------------------------------------------------------------------
    # Incoming client message dispatcher
    # ------------------------------------------------------------------
    async def dispatch_action(self, action: str, content: dict):
        if action == "send_message":
            await self.handle_send_message(content)
        elif action == "typing":
            await self.handle_typing(content)
        elif action == "read_messages":
            await self.handle_read_messages()
        else:
            await super().dispatch_action(action, content)

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------
    async def handle_send_message(self, content):
        body = content.get("body", "").strip()
        message_type = content.get("message_type", "text")
        if not body:
            await self.send_json({"error": "Message body cannot be empty."})
            return

        user = self.scope["user"]
        msg = await self.save_message(self.room_id, user, body, message_type)
        if not msg:
            await self.send_json(
                {"error": "Could not save message. Check room status."}
            )
            return

        await self.push(
            self.group_name,
            "chat_message",
            {
                "id": str(msg["id"]),
                "sender_email": user.email,
                "sender_name": f"{user.first_name} {user.last_name}".strip()
                or user.email,
                "message_type": message_type,
                "body": body,
                "created_at": msg["created_at"],
            },
        )

    async def handle_typing(self, content):
        user = self.scope["user"]
        await self.push(
            self.group_name,
            "chat_typing",
            {
                "sender": user.email,
                "is_typing": bool(content.get("is_typing", False)),
            },
        )

    async def handle_read_messages(self):
        user = self.scope["user"]
        await self.mark_messages_read(self.room_id, user)
        await self.push(self.group_name, "chat_read", {"reader": user.email})

    # ------------------------------------------------------------------
    # Channel layer event handlers (group → individual socket)
    # ------------------------------------------------------------------
    async def chat_message(self, event):
        payload = event["payload"]
        my_email = self.scope["user"].email
        payload = {**payload, "is_own": payload.get("sender_email") == my_email}
        await self.send_json({"type": "chat.message", "payload": payload})

    async def chat_typing(self, event):
        # Don't echo typing indicator back to the sender
        if event["payload"].get("sender") != self.scope["user"].email:
            await self.send_json({"type": "chat.typing", "payload": event["payload"]})

    async def chat_join(self, event):
        await self.send_json({"type": "chat.join", "payload": event["payload"]})

    async def chat_leave(self, event):
        await self.send_json({"type": "chat.leave", "payload": event["payload"]})

    async def chat_read(self, event):
        await self.send_json({"type": "chat.read", "payload": event["payload"]})

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------
    @database_sync_to_async
    def get_group_name(self, room_id):
        from apps.chat.models import ChatRoom

        return ChatRoom.objects.get(id=room_id).group_name

    @database_sync_to_async
    def can_access_room(self, user, room_id):
        from apps.chat.models import ChatRoom
        from django.contrib.auth.models import AnonymousUser

        if isinstance(user, AnonymousUser):
            return False
        if user.is_staff:
            return ChatRoom.objects.filter(id=room_id).exists()
        return (
            ChatRoom.objects.filter(id=room_id).filter(customer=user).exists()
            or ChatRoom.objects.filter(id=room_id, agent=user).exists()
        )

    @database_sync_to_async
    def save_message(self, room_id, user, body, message_type="text"):
        from apps.chat.models import ChatRoom, ChatMessage

        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.status in (ChatRoom.Status.RESOLVED, ChatRoom.Status.CLOSED):
                return None
            msg = ChatMessage.objects.create(
                room=room,
                sender=user,
                message_type=message_type,
                body=body,
            )
            # Touch room so it bubbles to top of list
            ChatRoom.objects.filter(id=room_id).update(updated_at=timezone.now())
            return {"id": msg.id, "created_at": msg.created_at.isoformat()}
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_message_history(self, room_id, user, limit=50):
        from apps.chat.models import ChatMessage

        messages = (
            ChatMessage.objects.filter(room_id=room_id)
            .select_related("sender")
            .order_by("-created_at")[:limit]
        )
        return [
            {
                "id": str(m.id),
                "sender_email": m.sender.email if m.sender else None,
                "sender_name": (
                    f"{m.sender.first_name} {m.sender.last_name}".strip()
                    if m.sender
                    else "System"
                ),
                "message_type": m.message_type,
                "body": m.body,
                "created_at": m.created_at.isoformat(),
                "is_own": m.sender_id == user.id if m.sender_id else False,
                "is_read": m.is_read,
            }
            for m in reversed(list(messages))
        ]

    @database_sync_to_async
    def mark_messages_read(self, room_id, user):
        from apps.chat.models import ChatMessage

        ChatMessage.objects.filter(room_id=room_id, is_read=False).exclude(
            sender=user
        ).update(is_read=True)
