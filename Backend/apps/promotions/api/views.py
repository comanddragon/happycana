# =============================================================================
# apps/promotions/api/views.py
# =============================================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.promotions.models import Coupon
from apps.storefronts.querysets import for_request
from .serializers import CouponSerializer, CouponValidateSerializer


class CouponListCreateView(generics.ListCreateAPIView):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(Coupon.objects.all(), self.request)

    def perform_create(self, serializer):
        serializer.save(storefront=getattr(self.request, "storefront", None))


class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(Coupon.objects.all(), self.request)


class ValidateCouponView(APIView):
    """Public endpoint — called during checkout to validate a coupon code."""

    def post(self, request):
        s = CouponValidateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        coupon = s.validated_data["coupon"]
        return Response(CouponSerializer(coupon).data, status=status.HTTP_200_OK)
