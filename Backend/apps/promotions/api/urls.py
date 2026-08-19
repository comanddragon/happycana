# =============================================================================
# apps/promotions/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("coupons/",              views.CouponListCreateView.as_view(), name="coupon-list"),
    path("coupons/<uuid:pk>/",   views.CouponDetailView.as_view(),     name="coupon-detail"),
    path("coupons/validate/",    views.ValidateCouponView.as_view(),   name="coupon-validate"),
]

