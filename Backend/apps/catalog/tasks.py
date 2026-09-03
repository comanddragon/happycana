
# =============================================================================
# apps/catalog/tasks.py
# =============================================================================
from django.tasks import task
from services.search import SearchService


@task()
def index_product(product_id: str):
    """Re-index a single product after a save."""
    from apps.catalog.models import Product
    try:
        product = Product.objects.prefetch_related("variants", "categories").get(id=product_id)
        SearchService.index_product(product)
    except Product.DoesNotExist:
        SearchService.delete_product(product_id)


@task()
def delete_product_from_index(product_id: str):
    """Remove a product from the search index after deletion."""
    SearchService.delete_product(product_id)


@task()
def reindex_all_products():
    """
    Nightly full reindex — run via cron or management command.
    Syncs the entire product catalogue with the search index.
    """
    from apps.catalog.models import Product
    products = (
        Product.objects
        .filter(is_active=True)
        .prefetch_related("categories", "variants")
    )
    SearchService.bulk_index_products(products)

