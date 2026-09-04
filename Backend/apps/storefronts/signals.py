from corsheaders.signals import check_request_enabled

from .models import StorefrontOrigin


def allow_storefront_origin(sender, request, **kwargs):
    origin = request.headers.get("origin", "").rstrip("/")
    if not origin:
        return False
    return StorefrontOrigin.objects.filter(
        origin=origin, storefront__is_active=True
    ).exists()


check_request_enabled.connect(allow_storefront_origin)
