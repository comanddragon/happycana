
# =============================================================================
# services/search.py
# Search indexing facade — decouples apps from the search backend.
# Swap MeiliSearch for Elasticsearch by only changing this file.
# =============================================================================
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SearchService:

    @staticmethod
    def _get_client():
        import meilisearch
        return meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY)

    # ------------------------------------------------------------------
    # Product indexing
    # ------------------------------------------------------------------

    @classmethod
    def index_product(cls, product):
        """Add or update a product in the search index."""
        try:
            client = cls._get_client()
            index  = client.index("products")
            doc    = cls._serialize_product(product)
            index.add_documents([doc])
            logger.info("Indexed product %s", product.id)
        except Exception as exc:
            logger.exception("Failed to index product %s: %s", product.id, exc)

    @classmethod
    def delete_product(cls, product_id):
        """Remove a product from the search index."""
        try:
            client = cls._get_client()
            client.index("products").delete_document(str(product_id))
            logger.info("Deleted product %s from index", product_id)
        except Exception as exc:
            logger.exception("Failed to delete product %s from index: %s", product_id, exc)

    @classmethod
    def bulk_index_products(cls, products):
        """Bulk-index a queryset of products — used by the nightly reindex task."""
        try:
            client = cls._get_client()
            index  = client.index("products")
            docs   = [cls._serialize_product(p) for p in products]
            index.add_documents(docs)
            logger.info("Bulk indexed %d products", len(docs))
        except Exception as exc:
            logger.exception("Bulk indexing failed: %s", exc)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @classmethod
    def search_products(cls, query, filters=None, limit=20, offset=0):
        """
        Search products and return raw MeiliSearch hits.
        filters example: "category = 'electronics' AND base_price < 500"
        """
        try:
            client  = cls._get_client()
            index   = client.index("products")
            options = {"limit": limit, "offset": offset}
            if filters:
                options["filter"] = filters
            result = index.search(query, options)
            return result.get("hits", [])
        except Exception as exc:
            logger.exception("Search failed for query '%s': %s", query, exc)
            return []

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_product(product):
        return {
            "id":          str(product.id),
            "name":        product.name,
            "slug":        product.slug,
            "description": product.description,
            "base_price":  float(product.base_price),
            "category":    product.category.name if product.category else None,
            "is_active":   product.is_active,
            "skus":        [v.sku for v in product.variants.all()],
        }

