
# =============================================================================
# apps/notifications/api/serializers.py
# =============================================================================
from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ["id", "type", "title", "body", "is_read", "created_at"]
        read_only_fields = ["id", "type", "title", "body", "created_at"]


class MarkReadSerializer(serializers.Serializer):
    """Accepts a list of notification IDs to mark as read in bulk."""
    ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)

    def validate_ids(self, value):
        user = self.context["request"].user
        found = Notification.objects.filter(id__in=value, user=user).count()
        if found != len(value):
            raise serializers.ValidationError("One or more notification IDs are invalid.")
        return value

    def save(self):
        Notification.objects.filter(
            id__in=self.validated_data["ids"]
        ).update(is_read=True)
