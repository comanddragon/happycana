# =============================================================================
# apps/analytics/api/views.py
# =============================================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from apps.analytics.models import Event, DailySalesSnapshot, ProductPerformance, ConversionFunnel
from .serializers import (
    EventIngestSerializer, DailySalesSnapshotSerializer,
    ProductPerformanceSerializer, ConversionFunnelSerializer,
)


class EventIngestView(APIView):
    """Receives frontend tracking events. Auth optional — also accepts anonymous."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request):
        s = EventIngestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(
            user       = request.user if request.user.is_authenticated else None,
            ip_address = request.META.get("REMOTE_ADDR"),
        )
        return Response(status=status.HTTP_201_CREATED)


class DailySalesSnapshotListView(generics.ListAPIView):
    serializer_class   = DailySalesSnapshotSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ["date"]
    ordering_fields    = ["date", "net_revenue", "total_orders"]
    ordering           = ["-date"]

    def get_queryset(self):
        qs = DailySalesSnapshot.objects.all()
        date_from = self.request.query_params.get("date_from")
        date_to   = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs


class ProductPerformanceListView(generics.ListAPIView):
    serializer_class   = ProductPerformanceSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ["product", "date"]
    ordering_fields    = ["date", "revenue", "purchases", "views"]
    ordering           = ["-date"]

    def get_queryset(self):
        return ProductPerformance.objects.select_related("product")


class ConversionFunnelListView(generics.ListAPIView):
    serializer_class   = ConversionFunnelSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends    = [filters.OrderingFilter]
    ordering_fields    = ["date"]
    ordering           = ["-date"]

    def get_queryset(self):
        qs = ConversionFunnel.objects.all()
        date_from = self.request.query_params.get("date_from")
        date_to   = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs