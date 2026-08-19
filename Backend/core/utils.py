# =============================================================================
# core/utils.py
# =============================================================================
import hashlib
from django.utils.text import slugify


def unique_slug(model_class, name, slug_field="slug"):
    """Generate a unique slug for a model, appending a counter if needed."""
    base  = slugify(name)
    slug  = base
    count = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base}-{count}"
        count += 1
    return slug


def mask_email(email: str) -> str:
    """Return a masked email for logging e.g. jo**@example.com"""
    local, domain = email.split("@")
    return f"{local[:2]}**@{domain}"


def hash_value(value: str) -> str:
    """SHA-256 hash of a string — useful for storing sensitive reference IDs."""
    return hashlib.sha256(value.encode()).hexdigest()