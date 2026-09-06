import pytest
from decimal import Decimal
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_current_storefront_returns_frontend_configuration():
    store = baker.make(
        "storefronts.Storefront",
        slug="peptides",
        currency="USD",
        branding={"logo": "https://cdn.example/logo.svg"},
    )

    response = APIClient().get("/api/storefront/", HTTP_X_STOREFRONT=store.slug)

    assert response.status_code == 200
    assert response.data["slug"] == "peptides"
    assert response.data["branding"] == {"logo": "https://cdn.example/logo.svg"}


@pytest.mark.django_db
def test_listing_detail_uses_storefront_slug_and_merchandising_overrides():
    product = baker.make(
        "catalog.Product",
        name="Shared Product",
        base_price=Decimal("20.00"),
        is_active=True,
    )
    peptides = baker.make("storefronts.Storefront", slug="peptides")
    footwear = baker.make("storefronts.Storefront", slug="footwear")
    listing = baker.make(
        "catalog.Listing",
        storefront=peptides,
        product=product,
        slug="peptide-special",
        title="Peptide Special",
        price_override=Decimal("15.00"),
        meta_title="Peptide SEO title",
        is_active=True,
    )
    baker.make(
        "catalog.Listing",
        storefront=footwear,
        product=product,
        slug="shoe-special",
        is_active=True,
    )

    response = APIClient().get(
        f"/api/catalog/listings/{listing.slug}/", HTTP_X_STOREFRONT=peptides.slug
    )
    cross_store = APIClient().get(
        "/api/catalog/listings/shoe-special/", HTTP_X_STOREFRONT=peptides.slug
    )

    assert response.status_code == 200
    assert response.data["display_name"] == "Peptide Special"
    assert response.data["effective_price"] == "15.00"
    assert response.data["meta_title"] == "Peptide SEO title"
    assert response.data["product"]["description"] == product.description
    assert cross_store.status_code == 404
