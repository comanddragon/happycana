
# =============================================================================
# apps/analytics/managers.py
# =============================================================================
from django.db import models as db_models


class EventQuerySet(db_models.QuerySet):

    def for_user(self, user):
        return self.filter(user=user)

    def for_session(self, session_key):
        return self.filter(session_key=session_key)

    def by_type(self, event_type):
        return self.filter(event_type=event_type)

    def on_date(self, date):
        return self.filter(occurred_at__date=date)

    def in_date_range(self, start, end):
        return self.filter(occurred_at__date__gte=start, occurred_at__date__lte=end)

    def anonymous(self):
        return self.filter(user__isnull=True)


class EventManager(db_models.Manager):
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def by_type(self, event_type):
        return self.get_queryset().by_type(event_type)

    def on_date(self, date):
        return self.get_queryset().on_date(date)


class DailySalesSnapshotQuerySet(db_models.QuerySet):

    def in_date_range(self, start, end):
        return self.filter(date__gte=start, date__lte=end)

    def latest_n(self, n):
        return self.order_by("-date")[:n]


class DailySalesSnapshotManager(db_models.Manager):
    def get_queryset(self):
        return DailySalesSnapshotQuerySet(self.model, using=self._db)

    def in_date_range(self, start, end):
        return self.get_queryset().in_date_range(start, end)

    def latest_n(self, n=30):
        return self.get_queryset().latest_n(n)


class ProductPerformanceQuerySet(db_models.QuerySet):

    def for_product(self, product_id):
        return self.filter(product_id=product_id)

    def in_date_range(self, start, end):
        return self.filter(date__gte=start, date__lte=end)

    def top_by_revenue(self, n=10):
        return self.order_by("-revenue")[:n]

    def top_by_views(self, n=10):
        return self.order_by("-views")[:n]


class ProductPerformanceManager(db_models.Manager):
    def get_queryset(self):
        return ProductPerformanceQuerySet(self.model, using=self._db)

    def for_product(self, product_id):
        return self.get_queryset().for_product(product_id)

    def top_by_revenue(self, n=10):
        return self.get_queryset().top_by_revenue(n)


# Integrate into apps/analytics/models.py:
#   Event.objects               = EventManager()
#   DailySalesSnapshot.objects  = DailySalesSnapshotManager()
#   ProductPerformance.objects  = ProductPerformanceManager()
