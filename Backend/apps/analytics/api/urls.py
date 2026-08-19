# =============================================================================
# apps/analytics/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("analytics/events/",      views.EventIngestView.as_view(),              name="event-ingest"),
    path("analytics/sales/",       views.DailySalesSnapshotListView.as_view(),   name="sales-snapshots"),
    path("analytics/products/",    views.ProductPerformanceListView.as_view(),   name="product-performance"),
    path("analytics/funnel/",      views.ConversionFunnelListView.as_view(),     name="conversion-funnel"),
]
