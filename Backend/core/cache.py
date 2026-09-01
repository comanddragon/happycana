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


# -----------------------------------------------------------------------
# Category tree cache versioning
# -----------------------------------------------------------------------
# The category tree endpoint (GET /api/catalog/categories/) serializes the
# *entire* active tree on every request via CategoryManager.attach_full_tree,
# even though the tree only changes when a category is created/edited/
# deleted (i.e. rarely, and always through the admin/API — never per
# storefront visit). Any given response is cheap to keep around; the win
# is not recomputing it for every request.
#
# Responses are keyed by request path + query string (so different filters/
# pages get distinct entries) plus a version number. Rather than tracking
# and deleting every key that's ever been cached (impossible without a
# separate index, since Category writes don't know which querystrings were
# requested), we bump the version on any Category write, which makes all
# previously cached keys unreachable; they then simply expire off of
# CATEGORY_TTL instead of being actively deleted.
CATEGORY_TREE_VERSION_KEY = "category:tree:version"


def get_category_tree_version():
    version = cache.get(CATEGORY_TREE_VERSION_KEY)
    if version is None:
        version = 1
        cache.set(CATEGORY_TREE_VERSION_KEY, version, timeout=None)
    return version


def bump_category_tree_version():
    try:
        cache.incr(CATEGORY_TREE_VERSION_KEY)
    except ValueError:
        # Key hadn't been set yet (e.g. cache was flushed) — seed it.
        cache.set(CATEGORY_TREE_VERSION_KEY, 1, timeout=None)


def get_category_tree_cache_key(request_path):
    return f"category:tree:v{get_category_tree_version()}:{request_path}"


def cache_category_tree_response(request_path, data):
    cache.set(get_category_tree_cache_key(request_path), data, timeout=CATEGORY_TTL)


def get_cached_category_tree_response(request_path):
    return cache.get(get_category_tree_cache_key(request_path))


