from django.db import migrations


def move_cannabis_fields_to_profiles(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    CannabisProfile = apps.get_model("catalog_cannabis", "CannabisProfile")

    for product in Product.objects.all().iterator():
        effect_ids = list(product.effects.values_list("id", flat=True))
        has_cannabis_data = bool(
            product.cannabis_type or product.compliance_category or product.sub_type
            or effect_ids or product.kind == "cannabis"
        )
        if not has_cannabis_data:
            continue
        profile, _ = CannabisProfile.objects.update_or_create(
            product_id=product.id,
            defaults={
                "cannabis_type": product.cannabis_type,
                "compliance_category": product.compliance_category,
                "sub_type": product.sub_type,
            },
        )
        profile.effect_tags.set(effect_ids)
        if product.kind != "cannabis":
            Product.objects.filter(pk=product.pk).update(kind="cannabis")


def restore_cannabis_fields_to_products(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    CannabisProfile = apps.get_model("catalog_cannabis", "CannabisProfile")

    for profile in CannabisProfile.objects.all().iterator():
        Product.objects.filter(pk=profile.product_id).update(
            cannabis_type=profile.cannabis_type,
            compliance_category=profile.compliance_category,
            sub_type=profile.sub_type,
        )
        product = Product.objects.get(pk=profile.product_id)
        product.effects.set(profile.effect_tags.values_list("id", flat=True))


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0018_product_kind_listing"),
        ("catalog_cannabis", "0002_remove_cannabisprofile_effects_and_more"),
    ]

    operations = [
        migrations.RunPython(move_cannabis_fields_to_profiles, restore_cannabis_fields_to_products),
        migrations.RemoveField(model_name="product", name="cannabis_type"),
        migrations.RemoveField(model_name="product", name="compliance_category"),
        migrations.RemoveField(model_name="product", name="effects"),
        migrations.RemoveField(model_name="product", name="sub_type"),
    ]
