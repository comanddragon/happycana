# =============================================================================
# apps/orders/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("orders/cart/",                           views.CartView.as_view(),             name="cart"),
    path("orders/cart/items/",                     views.CartItemAddView.as_view(),      name="cart-item-add"),
    path("orders/cart/items/<uuid:pk>/",           views.CartItemUpdateView.as_view(),   name="cart-item-detail"),
    path("orders/",                         views.OrderListView.as_view(),        name="order-list"),
    path("orders/checkout/",               views.OrderCreateView.as_view(),      name="order-create"),
    path("orders/<uuid:pk>/",              views.OrderDetailView.as_view(),      name="order-detail"),
    path("orders/<uuid:pk>/cancel/",       views.OrderCancelView.as_view(),      name="order-cancel"),
    path("orders/<uuid:pk>/status/",       views.OrderStatusUpdateView.as_view(),name="order-status"),
]

