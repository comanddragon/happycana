from urllib.parse import urlsplit

from .models import Storefront, StorefrontDomain, StorefrontOrigin


class StorefrontMiddleware:
    """Resolve the storefront selector; authorization remains view-specific.

    The slug header is a selector, not a trust boundary. Every private view
    must still enforce user/storefront membership and object ownership.
    """

    header_name = "HTTP_X_STOREFRONT"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.storefront = self.resolve(request)
        return self.get_response(request)

    @classmethod
    def resolve(cls, request):
        slug = request.META.get(cls.header_name, "").strip()
        if slug:
            return Storefront.objects.filter(slug=slug, is_active=True).first()

        origin = request.META.get("HTTP_ORIGIN", "").rstrip("/")
        if origin:
            match = StorefrontOrigin.objects.select_related("storefront").filter(
                origin=origin, storefront__is_active=True
            ).first()
            if match:
                return match.storefront

        host = urlsplit(f"//{request.get_host()}").hostname
        if not host:
            return None
        match = StorefrontDomain.objects.select_related("storefront").filter(
            domain=host.lower(), storefront__is_active=True
        ).first()
        return match.storefront if match else None
