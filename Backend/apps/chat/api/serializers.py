# =============================================================================
# apps/chat/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.chat.models import ChatRoom, ChatMessage
from apps.users.models import User


class ChatParticipantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ["id", "email", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class ChatMessageSerializer(serializers.ModelSerializer):
    sender      = ChatParticipantSerializer(read_only=True)
    is_own      = serializers.SerializerMethodField()

    class Meta:
        model  = ChatMessage
        fields = ["id", "room", "sender", "message_type", "body", "file", "is_read", "created_at", "is_own"]
        read_only_fields = ["id", "room", "sender", "created_at"]

    def get_is_own(self, obj):
        request = self.context.get("request")
        if request and obj.sender_id:
            return str(obj.sender_id) == str(request.user.id)
        return False


class ChatRoomSerializer(serializers.ModelSerializer):
    customer       = ChatParticipantSerializer(read_only=True)
    agent          = ChatParticipantSerializer(read_only=True)
    latest_message = serializers.SerializerMethodField()
    unread_count   = serializers.SerializerMethodField()

    class Meta:
        model  = ChatRoom
        fields = [
            "id", "customer", "agent", "order", "subject",
            "status", "created_at", "updated_at",
            "latest_message", "unread_count",
        ]
        read_only_fields = ["id", "customer", "created_at", "updated_at"]

    def get_latest_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {"body": msg.body, "created_at": msg.created_at.isoformat(), "type": msg.message_type}
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()


class CreateChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatRoom
        fields = ["subject", "order"]

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)


class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = ["body", "message_type", "file"]

    def create(self, validated_data):
        validated_data["sender"] = self.context["request"].user
        validated_data["room"]   = self.context["room"]
        return super().create(validated_data)