
# =============================================================================
# apps/inventory/managers.py
# =============================================================================
from django.db import models as db_models


class StockQuerySet(db_models.QuerySet):

    def for_variant(self, variant_id):
        return self.filter(variant_id=variant_id)

    def for_warehouse(self, warehouse_id):
        return self.filter(warehouse_id=warehouse_id)

    def with_variant(self):
        return self.select_related("variant__product")

    def with_warehouse(self):
        return self.select_related("warehouse")

    def full(self):
        return self.with_variant().with_warehouse()

    def available(self):
        """Stock records with at least 1 available unit."""
        return self.filter(quantity__gt=db_models.F("reserved"))

    def low(self, threshold=5):
        """Stock records at or below the low-stock threshold."""
        return self.filter(
            quantity__gt=db_models.F("reserved"),
            quantity__lte=db_models.F("reserved") + threshold,
        )

    def out_of_stock(self):
        return self.filter(quantity__lte=db_models.F("reserved"))


class StockManager(db_models.Manager):
    def get_queryset(self):
        return StockQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def low(self, threshold=5):
        return self.get_queryset().low(threshold=threshold)

    def out_of_stock(self):
        return self.get_queryset().out_of_stock()


class StockMovementQuerySet(db_models.QuerySet):

    def for_stock(self, stock_id):
        return self.filter(stock_id=stock_id)

    def sales(self):
        return self.filter(reason="sale")

    def returns(self):
        return self.filter(reason="return")

    def adjustments(self):
        return self.filter(reason="adjustment")

    def in_date_range(self, start, end):
        return self.filter(created_at__date__gte=start, created_at__date__lte=end)


class StockMovementManager(db_models.Manager):
    def get_queryset(self):
        return StockMovementQuerySet(self.model, using=self._db)

    def for_stock(self, stock_id):
        return self.get_queryset().for_stock(stock_id)


# Integrate into apps/inventory/models.py:
#   Stock.objects         = StockManager()
#   StockMovement.objects = StockMovementManager()

