# =============================================================================
# apps/inventory/api/views.py
# =============================================================================
from rest_framework import generics, permissions
from apps.inventory.models import Warehouse, Stock, StockMovement
from apps.storefronts.querysets import for_request
from .serializers import (
    WarehouseSerializer,
    StockSerializer,
    StockWriteSerializer,
    StockMovementSerializer,
)


class WarehouseListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(Warehouse.objects.filter(is_active=True), self.request)

    def perform_create(self, serializer):
        serializer.save(storefront=getattr(self.request, "storefront", None))


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(Warehouse.objects.all(), self.request)


class StockListView(generics.ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = for_request(
            Stock.objects.select_related("variant", "warehouse"),
            self.request,
            "warehouse__storefront",
        )
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        return qs


class StockDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(
            Stock.objects.select_related("variant", "warehouse"),
            self.request,
            "warehouse__storefront",
        )

    def get_serializer_class(self):
        return (
            StockWriteSerializer
            if self.request.method in ("PUT", "PATCH")
            else StockSerializer
        )


class StockMovementListView(generics.ListCreateAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return for_request(
            StockMovement.objects.filter(stock_id=self.kwargs["stock_pk"]),
            self.request,
            "stock__warehouse__storefront",
        ).order_by("-created_at")

    def perform_create(self, serializer):
        movement = serializer.save(stock_id=self.kwargs["stock_pk"])
        # Apply the delta to the stock quantity
        stock = movement.stock
        stock.quantity += movement.quantity_delta
        stock.save(update_fields=["quantity"])
