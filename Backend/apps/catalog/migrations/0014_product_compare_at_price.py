from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0013_category_is_key_product_categories_m2m")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="compare_at_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
