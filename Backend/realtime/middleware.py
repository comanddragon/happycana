
# =============================================================================
# realtime/middleware.py
# =============================================================================
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user_from_token(token_key):
    from apps.users.models import User
    try:
        token = AccessToken(token_key)
        return User.objects.get(id=token["user_id"])
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Authenticates WebSocket connections via a JWT token passed as
    a query parameter:  ws://host/ws/orders/123/?token=<access_token>
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params       = parse_qs(query_string)
        token_key    = params.get("token", [None])[0]
        scope["user"] = await get_user_from_token(token_key) if token_key else AnonymousUser()
        return await super().__call__(scope, receive, send)