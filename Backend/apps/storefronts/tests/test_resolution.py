import pytest
from django.test import RequestFactory
from django.test.utils import override_settings

from apps.storefronts.middleware import StorefrontMiddleware
from apps.storefronts.models import Storefront, StorefrontDomain, StorefrontOrigin


@pytest.mark.django_db
def test_resolves_storefront_from_explicit_slug():
    store = Storefront.objects.create(slug="peptides", name="Peptides")
    request = RequestFactory().get("/api/storefront/", HTTP_X_STOREFRONT="peptides")

    assert StorefrontMiddleware.resolve(request) == store


@pytest.mark.django_db
def test_resolves_storefront_from_browser_origin():
    store = Storefront.objects.create(slug="footwear", name="Footwear")
    StorefrontOrigin.objects.create(storefront=store, origin="https://shoes.example.com")
    request = RequestFactory().get(
        "/api/storefront/", HTTP_ORIGIN="https://shoes.example.com/"
    )

    assert StorefrontMiddleware.resolve(request) == store


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=["api.dispensary.example.com"])
def test_resolves_storefront_from_api_domain():
    store = Storefront.objects.create(slug="dispensary", name="Dispensary")
    StorefrontDomain.objects.create(storefront=store, domain="API.DISPENSARY.EXAMPLE.COM.")
    request = RequestFactory().get(
        "/api/storefront/", HTTP_HOST="api.dispensary.example.com"
    )

    assert StorefrontMiddleware.resolve(request) == store
