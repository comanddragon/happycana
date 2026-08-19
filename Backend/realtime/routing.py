# =============================================================================
# realtime/routing.py
# =============================================================================
from django.urls import re_path
from .consumers import (
    order_status,
    inventory,
    notifications,
    chat,
)

websocket_urlpatterns = [
    re_path(r"^ws/orders/(?P<order_id>[0-9a-f-]+)/$", order_status.OrderStatusConsumer.as_asgi()),
    re_path(r"^ws/inventory/$", inventory.InventoryConsumer.as_asgi()),
    re_path(r"^ws/notifications/$", notifications.NotificationConsumer.as_asgi()),
    re_path(r"^ws/chat/(?P<room_id>[0-9a-f-]+)/$", chat.ChatConsumer.as_asgi()),
]

