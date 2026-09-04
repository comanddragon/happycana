# =============================================================================
# apps/shipping/api/views.py
# =============================================================================
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from core.permissions import IsOwnerOrAdmin
from apps.shipping.models import Shipment, ShippingMethod, TrackingEvent
from apps.storefronts.querysets import for_request
from .serializers import (
    ShipmentSerializer,
    ShipmentUpdateSerializer,
    ShippingMethodSerializer,
    TrackingEventSerializer,
)


# ── Shipping Methods ───────────────────────────────────────────────────────────


class ShippingMethodListView(generics.ListCreateAPIView):
    """
    GET  — public; returns only active methods (for checkout dropdowns).
    POST — admin only; creates a new shipping method.
    """

    serializer_class = ShippingMethodSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = for_request(ShippingMethod.objects.all(), self.request)
        # Non-admins only see active methods
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(storefront=getattr(self.request, "storefront", None))


class ShippingMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — public (customers can deep-link to a method).
    PUT / PATCH / DELETE — admin only.
    """

    serializer_class = ShippingMethodSerializer

    def get_queryset(self):
        return for_request(ShippingMethod.objects.all(), self.request)

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


# ── Shipments ──────────────────────────────────────────────────────────────────


class ShipmentListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return (
            for_request(Shipment.objects, self.request, "order__storefront")
            .select_related("order", "warehouse", "shipping_method")
            .prefetch_related("events")
        )


class ShipmentDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return (
            for_request(Shipment.objects, self.request, "order__storefront")
            .select_related("order", "warehouse", "shipping_method")
            .prefetch_related("events")
        )

    def get_serializer_class(self):
        return (
            ShipmentUpdateSerializer
            if self.request.method in ("PUT", "PATCH")
            else ShipmentSerializer
        )

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj.order.user != self.request.user:
            raise PermissionDenied
        return obj


class OrderShipmentListView(generics.ListAPIView):
    """Lists all shipments for a specific order."""

    serializer_class = ShipmentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        order_pk = self.kwargs["order_pk"]

        if not self.request.user.is_staff:
            from apps.orders.models import Order

            try:
                for_request(Order.objects, self.request).get(
                    id=order_pk, user=self.request.user
                )
            except Order.DoesNotExist:
                raise NotFound  # 404 rather than leaking that the order exists

        return (
            for_request(Shipment.objects, self.request, "order__storefront")
            .filter(order_id=order_pk)
            .select_related("shipping_method")
            .prefetch_related("events")
        )


# ── Tracking ───────────────────────────────────────────────────────────────────


class TrackingEventListView(generics.ListAPIView):
    """Public tracking — accessible by anyone with a valid shipment ID."""

    serializer_class = TrackingEventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            for_request(
                TrackingEvent.objects, self.request, "shipment__order__storefront"
            )
            .filter(shipment_id=self.kwargs["shipment_pk"])
            .order_by("-occurred_at")
        )
