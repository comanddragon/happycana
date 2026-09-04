def for_request(queryset, request, field="storefront"):
    """Scope a queryset to the storefront selected by middleware.

    Requests without a selector intentionally see only legacy/global rows.
    This keeps the existing frontend working while preventing it from
    accidentally crossing into a configured storefront.
    """
    return queryset.filter(**{field: getattr(request, "storefront", None)})
