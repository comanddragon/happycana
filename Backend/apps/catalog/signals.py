# =============================================================================
# apps/catalog/signals.py  — Invalidates the category tree cache on writes
# =============================================================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.catalog.models import Category
from core.cache import bump_category_tree_version


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_tree_cache(sender, instance, **kwargs):
    bump_category_tree_version()
