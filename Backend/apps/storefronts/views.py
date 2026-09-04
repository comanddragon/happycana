from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import StorefrontSerializer


class CurrentStorefrontView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        storefront = getattr(request, "storefront", None)
        if storefront is None:
            raise NotFound("No active storefront matches this request.")
        return Response(StorefrontSerializer(storefront).data)
