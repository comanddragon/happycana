# =============================================================================
# apps/chat/api/views.py
# =============================================================================
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Prefetch, Q
from apps.chat.models import ChatRoom, ChatMessage
from .serializers import (
    ChatRoomSerializer, CreateChatRoomSerializer,
    ChatMessageSerializer, SendMessageSerializer,
)


class IsParticipant(permissions.BasePermission):
    """Allow access only to the customer, assigned agent, or staff."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        if isinstance(obj, ChatRoom):
            return obj.customer_id == user.id or obj.agent_id == user.id
        if isinstance(obj, ChatMessage):
            return (
                obj.room.customer_id == user.id or
                obj.room.agent_id    == user.id
            )
        return False


class ChatRoomViewSet(ModelViewSet):
    """
    Customers see their own rooms; staff sees all (filterable by status).

    GET    /api/chat/rooms/           — list rooms
    POST   /api/chat/rooms/           — open a new room
    GET    /api/chat/rooms/{id}/      — room detail
    PATCH  /api/chat/rooms/{id}/      — update subject / status
    GET    /api/chat/rooms/{id}/messages/   — paginated message history
    POST   /api/chat/rooms/{id}/messages/   — post a message via REST (fallback)
    POST   /api/chat/rooms/{id}/assign/     — staff: assign agent
    POST   /api/chat/rooms/{id}/resolve/    — resolve room
    """
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        user = self.request.user
        # Prefetch exactly what ChatRoomSerializer.get_latest_message /
        # get_unread_count need, via to_attr, so those methods can read from
        # the cache instead of each issuing a fresh query per room
        # (.last()/.filter() on a related manager bypass prefetch_related's
        # cache and re-hit the DB otherwise).
        qs = ChatRoom.objects.select_related("customer", "agent", "order").prefetch_related(
            Prefetch(
                "messages",
                queryset=ChatMessage.objects.order_by("-created_at"),
                to_attr="_latest_message_list",
            ),
            Prefetch(
                "messages",
                queryset=ChatMessage.objects.filter(is_read=False).exclude(sender=user),
                to_attr="_unread_messages",
            ),
        )
        if user.is_staff:
            status_filter = self.request.query_params.get("status")
            if status_filter:
                qs = qs.filter(status=status_filter)
            return qs.order_by("-updated_at")
        return qs.filter(Q(customer=user) | Q(agent=user)).order_by("-updated_at")

    def get_serializer_class(self):
        if self.action == "create":
            return CreateChatRoomSerializer
        return ChatRoomSerializer

    # ------------------------------------------------------------------
    # /rooms/{id}/messages/
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        room = self.get_object()

        if request.method == "GET":
            qs = room.messages.select_related("sender").order_by("created_at")
            # Mark all as read for this user
            qs.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
            serializer = ChatMessageSerializer(qs, many=True, context={"request": request})
            return Response(serializer.data)

        # POST — send a message via REST (WebSocket is preferred; this is a fallback)
        serializer = SendMessageSerializer(
            data=request.data, context={"request": request, "room": room}
        )
        serializer.is_valid(raise_exception=True)
        msg = serializer.save()

        # Broadcast via channel layer so WS clients get it too
        _broadcast_message(room, msg)

        return Response(ChatMessageSerializer(msg, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # /rooms/{id}/assign/
    # ------------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="assign",
            permission_classes=[permissions.IsAdminUser])
    def assign(self, request, pk=None):
        room       = self.get_object()
        agent_id   = request.data.get("agent_id")
        try:
            from apps.users.models import User
            agent = User.objects.get(id=agent_id, is_staff=True)
        except Exception:
            return Response({"detail": "Agent not found."}, status=status.HTTP_400_BAD_REQUEST)
        room.agent  = agent
        room.status = ChatRoom.Status.ASSIGNED
        room.save(update_fields=["agent", "status", "updated_at"])
        _system_message(room, f"Agent {agent.email} has joined the chat.")
        return Response(ChatRoomSerializer(room, context={"request": request}).data)

    # ------------------------------------------------------------------
    # /rooms/{id}/resolve/
    # ------------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        room = self.get_object()
        if room.status == ChatRoom.Status.CLOSED:
            return Response({"detail": "Room is already closed."}, status=status.HTTP_400_BAD_REQUEST)
        room.status = ChatRoom.Status.RESOLVED
        room.save(update_fields=["status", "updated_at"])
        _system_message(room, "This conversation has been marked as resolved.")
        return Response(ChatRoomSerializer(room, context={"request": request}).data)

# ------------------------------------------------------------------
# Internal helpers (not views)
# ------------------------------------------------------------------
def _broadcast_message(room, msg):
    """Push a new chat message to all WS clients in the room."""
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room.group_name,
        {
            "type": "chat_message",
            "payload": {
                "id":           str(msg.id),
                "sender_email": msg.sender.email if msg.sender else None,
                "sender_name":  (
                    f"{msg.sender.first_name} {msg.sender.last_name}".strip()
                    if msg.sender else "System"
                ),
                "message_type": msg.message_type,
                "body":         msg.body,
                "created_at":   msg.created_at.isoformat(),
            },
        },
    )


def _system_message(room, text):
    """Create a system ChatMessage and broadcast it."""
    msg = ChatMessage.objects.create(
        room=room, sender=None,
        message_type=ChatMessage.MessageType.SYSTEM,
        body=text,
    )
    _broadcast_message(room, msg)
    return msg