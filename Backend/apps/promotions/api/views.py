# =============================================================================
# apps/promotions/api/views.py
# =============================================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.promotions.models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer


class CouponListCreateView(generics.ListCreateAPIView):
    queryset           = Coupon.objects.all()
    serializer_class   = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Coupon.objects.all()
    serializer_class   = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


class ValidateCouponView(APIView):
    """Public endpoint — called during checkout to validate a coupon code."""
    def post(self, request):
        s = CouponValidateSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        coupon = s.validated_data["coupon"]
        return Response(CouponSerializer(coupon).data, status=status.HTTP_200_OK)
