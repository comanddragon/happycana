# =============================================================================
# core/mixins.py
# =============================================================================
from django.utils import timezone


class SoftDeleteMixin:
    """
    Adds soft-delete behaviour to any model.
    Call obj.soft_delete() instead of obj.delete().
    Filter active records with Model.objects.filter(deleted_at__isnull=True).
    """
    # Add `deleted_at = models.DateTimeField(null=True, blank=True)` to your model.

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


