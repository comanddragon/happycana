# =============================================================================
# apps/shipping/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    # ── Shipping methods (checkout dropdown + admin CRUD) ──────────────────
    path("shipping/methods/",            views.ShippingMethodListView.as_view(),   name="shipping-method-list"),
    path("shipping-methods/<uuid:pk>/",  views.ShippingMethodDetailView.as_view(), name="shipping-method-detail"),

    # ── Shipments ──────────────────────────────────────────────────────────
    path("shipments/",                                      views.ShipmentListView.as_view(),      name="shipment-list"),
    path("shipments/<uuid:pk>/",                            views.ShipmentDetailView.as_view(),    name="shipment-detail"),
    path("shipments/<uuid:shipment_pk>/tracking/",          views.TrackingEventListView.as_view(), name="tracking-list"),
    path("orders/<uuid:order_pk>/shipments/",               views.OrderShipmentListView.as_view(), name="order-shipment-list"),
]
