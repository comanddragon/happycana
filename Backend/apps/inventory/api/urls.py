# =============================================================================
# apps/inventory/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("warehouses/",                                   views.WarehouseListCreateView.as_view(),  name="warehouse-list"),
    path("warehouses/<uuid:pk>/",                        views.WarehouseDetailView.as_view(),      name="warehouse-detail"),
    path("stock/",                                        views.StockListView.as_view(),            name="stock-list"),
    path("stock/<uuid:pk>/",                             views.StockDetailView.as_view(),          name="stock-detail"),
    path("stock/<uuid:stock_pk>/movements/",             views.StockMovementListView.as_view(),    name="stock-movement-list"),
]
