# =============================================================================
# apps/notifications/api/views.py
# =============================================================================
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.notifications.models import Notification
from apps.storefronts.querysets import for_request
from .serializers import NotificationSerializer, MarkReadSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
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
    def post(self, request):
        s = MarkReadSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response(
            {"detail": "Notifications marked as read."}, status=status.HTTP_200_OK
        )


class MarkAllNotificationsReadView(APIView):
    def post(self, request):
        for_request(
            Notification.objects.filter(user=request.user, is_read=False), request
        ).update(is_read=True)
        return Response(
            {"detail": "All notifications marked as read."}, status=status.HTTP_200_OK
        )
