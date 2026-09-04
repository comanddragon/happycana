from django.db import migrations


KEY_SLUGS = (
    "flower",
    "edibles",
    "pre-rolls",
    "vaporizers",
    "concentrates",
    "tinctures",
    "topicals",
    "beverages",
    "accessories",
    "cbd-products",
)


def promote_to_roots(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.filter(slug__in=KEY_SLUGS).update(parent=None, is_key=True)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0015_key_category_descriptions")]

    operations = [migrations.RunPython(promote_to_roots, migrations.RunPython.noop)]
