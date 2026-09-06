from django.db.models import Q


def for_request(queryset, request, field="storefront"):
    """Scope a queryset to the storefront selected by middleware.

    Requests without a selector intentionally see only legacy/global rows.
    This keeps the existing frontend working while preventing it from
    accidentally crossing into a configured storefront.
    """
    return queryset.filter(**{field: getattr(request, "storefront", None)})


def options_for_request(queryset, request, field="storefronts"):
    """Return global configuration rows plus rows owned by this storefront.

    This is intentionally only for reusable checkout options. Tenant-owned
    business data must continue to use ``for_request``.
    """
    storefront = getattr(request, "storefront", None)
    if storefront is None:
        return queryset.filter(is_global=True)
    return queryset.filter(
        Q(is_global=True) | Q(**{field: storefront})
    ).distinct()
