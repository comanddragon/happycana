# =============================================================================
# apps/chat/api/urls.py
# =============================================================================
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet

router = DefaultRouter()
router.register("chat/rooms", ChatRoomViewSet, basename="chat-room")
urlpatterns = router.urls
