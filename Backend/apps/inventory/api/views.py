# =============================================================================
# apps/inventory/api/views.py
# =============================================================================
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.inventory.models import Warehouse, Stock, StockMovement
from .serializers import (
    WarehouseSerializer, StockSerializer, StockWriteSerializer, StockMovementSerializer,
)


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset           = Warehouse.objects.filter(is_active=True)
    serializer_class   = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Warehouse.objects.all()
    serializer_class   = WarehouseSerializer
    permission_classes = [permissions.IsAdminUser]


class StockListView(generics.ListAPIView):
    serializer_class   = StockSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = Stock.objects.select_related("variant", "warehouse")
        warehouse = self.request.query_params.get("warehouse")
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        return qs


class StockDetailView(generics.RetrieveUpdateAPIView):
    queryset           = Stock.objects.select_related("variant", "warehouse")
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        return StockWriteSerializer if self.request.method in ("PUT", "PATCH") else StockSerializer


class StockMovementListView(generics.ListCreateAPIView):
    serializer_class   = StockMovementSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return StockMovement.objects.filter(stock_id=self.kwargs["stock_pk"]).order_by("-created_at")

    def perform_create(self, serializer):
        movement = serializer.save(stock_id=self.kwargs["stock_pk"])
        # Apply the delta to the stock quantity
        stock = movement.stock
        stock.quantity += movement.quantity_delta
        stock.save(update_fields=["quantity"])