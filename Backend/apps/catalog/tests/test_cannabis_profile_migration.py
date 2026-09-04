import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_cannabis_extraction_migration_preserves_existing_values():
    executor = MigrationExecutor(connection)
    latest_targets = executor.loader.graph.leaf_nodes()
    old_targets = [
        ("catalog", "0018_product_kind_listing"),
        ("catalog_cannabis", "0001_initial"),
    ]
    executor.migrate(old_targets)
    old_apps = executor.loader.project_state(old_targets).apps

    Product = old_apps.get_model("catalog", "Product")
    Effect = old_apps.get_model("catalog", "Effect")
    product = Product.objects.create(
        name="Legacy Flower",
        slug="legacy-flower",
        base_price="25.00",
        cannabis_type="indica",
        compliance_category="flower",
        sub_type="indoor",
    )
    effect = Effect.objects.create(name="Relaxed", slug="relaxed")
    product.effects.add(effect)

    executor = MigrationExecutor(connection)
    executor.migrate(latest_targets)
    new_apps = executor.loader.project_state(latest_targets).apps
    MigratedProduct = new_apps.get_model("catalog", "Product")
    CannabisProfile = new_apps.get_model("catalog_cannabis", "CannabisProfile")
    migrated_product = MigratedProduct.objects.get(pk=product.pk)
    profile = CannabisProfile.objects.get(product_id=product.pk)

    assert migrated_product.kind == "cannabis"
    assert profile.cannabis_type == "indica"
    assert profile.compliance_category == "flower"
    assert profile.sub_type == "indoor"
    assert list(profile.effect_tags.values_list("slug", flat=True)) == ["relaxed"]
