import pytest
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
