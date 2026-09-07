# =============================================================================
# apps/notifications/api/views.py
# =============================================================================
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.storefronts.querysets import for_request

from .serializers import MarkReadSerializer, NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        qs = for_request(
            Notification.objects.filter(user=self.request.user), self.request
        )
        unread_only = self.request.query_params.get("unread")
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs


class NotificationDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return for_request(
            Notification.objects.filter(user=self.request.user), self.request
        )


class MarkNotificationsReadView(APIView):
    serializer_class = MarkReadSerializer

    def post(self, request):
        s = MarkReadSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(
            {"detail": "Notifications marked as read."}, status=status.HTTP_200_OK
        )


class MarkAllNotificationsReadView(APIView):
    @extend_schema(request=None, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        for_request(
            Notification.objects.filter(user=request.user, is_read=False), request
        ).update(is_read=True)
        return Response(
            {"detail": "All notifications marked as read."}, status=status.HTTP_200_OK
        )
