# =============================================================================
# core/permissions.py
# =============================================================================
from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Full access for admin users; read-only for everyone else."""
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """Object-level: only the owner or an admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        owner = getattr(obj, "user", None) or getattr(obj, "owner", None)
        return owner == request.user


