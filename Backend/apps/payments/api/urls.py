# =============================================================================
# apps/payments/api/urls.py
# =============================================================================
from django.urls import path
from . import views

urlpatterns = [
    path("payments/",                              views.PaymentListView.as_view(),       name="payment-list"),
    path("payments/<uuid:pk>/",                   views.PaymentDetailView.as_view(),     name="payment-detail"),
    path("payments/orders/<uuid:order_pk>/pay/",  views.InitiatePaymentView.as_view(),   name="payment-initiate"),
    path("payments/refunds/",                     views.RefundCreateView.as_view(),      name="refund-create"),
    path("payments/webhooks/stripe/",             views.StripeWebhookView.as_view(),     name="stripe-webhook"),
    path("payments/webhooks/paypal/", views.PayPalWebhookView.as_view(), name="paypal-webhook"),
]

