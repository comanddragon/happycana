from django.db import migrations


CATEGORIES = {
    "flower": (
        "Cannabis Flower",
        "Shop fresh cannabis flower across indica, sativa, and hybrid strains from trusted growers.",
    ),
    "edibles": (
        "Cannabis Edibles",
        "Explore gummies, chews, chocolates, and other precisely dosed cannabis edibles.",
    ),
    "pre-rolls": (
        "Cannabis Pre-Rolls",
        "Ready-to-enjoy joints and infused pre-rolls in convenient single and multipack formats.",
    ),
    "vaporizers": (
        "Cannabis Vapes",
        "Browse vape cartridges, disposables, pods, and all-in-one cannabis vaporizers.",
    ),
    "concentrates": (
        "Cannabis Concentrates",
        "Discover live resin, rosin, hash, badder, sugar, and other potent concentrates.",
    ),
    "tinctures": (
        "Cannabis Tinctures",
        "Shop discreet, measured cannabis tinctures and drops for flexible daily dosing.",
    ),
    "topicals": (
        "Cannabis Topicals",
        "Explore cannabis-infused creams, balms, lotions, and targeted topical products.",
    ),
    "beverages": (
        "Cannabis Beverages",
        "Find refreshing cannabis drinks, seltzers, shots, and drink enhancers.",
    ),
    "accessories": (
        "Cannabis Accessories",
        "Shop practical accessories for storing, preparing, and enjoying cannabis products.",
    ),
    "cbd-products": (
        "CBD Products",
        "Browse CBD-forward flower, edibles, tinctures, topicals, and wellness products.",
    ),
}


def set_key_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.filter(is_key=True).update(is_key=False)
    for slug, (meta_title, description) in CATEGORIES.items():
        Category.objects.filter(slug=slug).update(
            is_key=True,
            description=description,
            meta_title=meta_title,
            meta_description=description[:160],
        )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0014_product_compare_at_price")]

    operations = [migrations.RunPython(set_key_categories, migrations.RunPython.noop)]
