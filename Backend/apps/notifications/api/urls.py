# =============================================================================
# apps/notifications/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("notifications/",                     views.NotificationListView.as_view(),         name="notification-list"),
    path("notifications/<uuid:pk>/",           views.NotificationDetailView.as_view(),       name="notification-detail"),
    path("notifications/mark-read/",           views.MarkNotificationsReadView.as_view(),    name="notification-mark-read"),
    path("notifications/mark-all-read/",       views.MarkAllNotificationsReadView.as_view(), name="notification-mark-all-read"),
]
