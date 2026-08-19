import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings.development")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from realtime.middleware import JWTAuthMiddleware
from realtime.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http":      get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
