"""Reusable visual helpers for Django admin list pages."""

from django.utils.html import format_html


def image_thumbnail(url: str, alt: str) -> str:
    """Render a compact list thumbnail or a neutral missing-image state."""
    if url:
        return format_html(
            '<span class="admin-thumbnail">'
            '<img src="{}" alt="{}" width="48" height="48" loading="lazy">'
            "</span>",
            url,
            alt,
        )

    return format_html(
        '<span class="admin-thumbnail admin-thumbnail--empty" '
        'role="img" aria-label="No image">'
        '<span class="material-symbols-outlined" aria-hidden="true">{}</span>'
        "</span>",
        "image_not_supported",
    )
