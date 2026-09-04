from decimal import Decimal

import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from apps.catalog.models import Listing


@pytest.mark.django_db
def test_listing_endpoint_only_returns_selected_storefront():
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    peptide_listing = Listing.objects.create(
        storefront=peptides,
        product=baker.make("catalog.Product", base_price=Decimal("25.00")),
        slug="peptide-a",
    )
    Listing.objects.create(
        storefront=footwear,
        product=baker.make("catalog.Product", base_price=Decimal("125.00")),
        slug="shoe-a",
    )

    response = APIClient().get("/api/catalog/listings/", HTTP_X_STOREFRONT="peptides")

    assert response.status_code == 200
    assert [item["id"] for item in response.data["results"]] == [str(peptide_listing.id)]


@pytest.mark.django_db
def test_listing_detail_cannot_cross_storefront_boundary():
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    Listing.objects.create(
        storefront=footwear,
        product=baker.make("catalog.Product"),
        slug="shoe-a",
    )

    response = APIClient().get(
        "/api/catalog/listings/shoe-a/", HTTP_X_STOREFRONT=peptides.slug
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_listing_endpoint_requires_a_storefront_selector():
    response = APIClient().get("/api/catalog/listings/")

    assert response.status_code == 400
