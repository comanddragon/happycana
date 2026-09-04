from django.urls import path

from .views import CurrentStorefrontView


urlpatterns = [
    path("storefront/", CurrentStorefrontView.as_view(), name="current-storefront"),
]
