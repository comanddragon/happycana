# =============================================================================
# apps/blog/signals.py — Invalidates the blog response cache on writes
# =============================================================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.blog.models import BlogPost
from core.cache import bump_blog_version


@receiver(post_save, sender=BlogPost)
@receiver(post_delete, sender=BlogPost)
def invalidate_blog_cache(sender, instance, **kwargs):
    bump_blog_version()
