from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0018_product_kind_listing"),
        ("catalog_cannabis", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(model_name="cannabisprofile", old_name="product_type", new_name="compliance_category"),
        migrations.RenameField(model_name="cannabisprofile", old_name="strain_type", new_name="cannabis_type"),
        migrations.RenameField(model_name="cannabisprofile", old_name="effects", new_name="effects_legacy"),
        migrations.AlterField(
            model_name="cannabisprofile", name="compliance_category",
            field=models.CharField(
                blank=True, max_length=20,
                choices=[
                    ("flower", "Flower"), ("vaporizers", "Vaporizers"),
                    ("edibles", "Edibles"), ("concentrates", "Concentrates"),
                    ("pre_rolls", "Pre-Rolls"), ("tinctures", "Tinctures"),
                    ("topicals", "Topicals"), ("beverages", "Beverages"),
                    ("accessories", "Accessories"), ("merchandise", "Merchandise"),
                    ("cbd_products", "CBD Products"), ("gift_cards", "Gift Cards"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cannabisprofile", name="cannabis_type",
            field=models.CharField(
                blank=True, max_length=20,
                choices=[
                    ("sativa", "Sativa"), ("indica", "Indica"),
                    ("hybrid", "Hybrid"),
                    ("hybrid_sativa", "Hybrid (Sativa Leaning)"),
                    ("hybrid_indica", "Hybrid (Indica Leaning)"),
                    ("na", "N/A"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="cannabisprofile", name="sub_type",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="cannabisprofile", name="effect_tags",
            field=models.ManyToManyField(blank=True, related_name="cannabis_profiles", to="catalog.effect"),
        ),
    ]
