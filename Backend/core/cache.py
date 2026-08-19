# =============================================================================
# core/cache.py
# =============================================================================
from django.core.cache import cache

PRODUCT_TTL  = 60 * 60       # 1 hour
CATEGORY_TTL = 60 * 60 * 6   # 6 hours


def get_product_cache_key(product_id):
    return f"product:{product_id}"

def get_category_cache_key(category_id):
    return f"category:{category_id}"

def cache_product(product_id, data):
    cache.set(get_product_cache_key(product_id), data, timeout=PRODUCT_TTL)

def get_cached_product(product_id):
    return cache.get(get_product_cache_key(product_id))

def invalidate_product(product_id):
    cache.delete(get_product_cache_key(product_id))

def cache_category(category_id, data):
    cache.set(get_category_cache_key(category_id), data, timeout=CATEGORY_TTL)

def get_cached_category(category_id):
    return cache.get(get_category_cache_key(category_id))

def invalidate_category(category_id):
    cache.delete(get_category_cache_key(category_id))


