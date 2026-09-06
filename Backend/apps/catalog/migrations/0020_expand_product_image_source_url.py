from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0019_remove_product_cannabis_type_and_more")]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="source_url",
            field=models.URLField(
                blank=True,
                max_length=1000,
                help_text="Passed through as-is from the source — not downloaded/re-hosted.",
            ),
        ),
    ]
