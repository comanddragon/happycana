from django.db import models as db_models


class CategoryQuerySet(db_models.QuerySet):
    def active(self):           return self.filter(is_active=True)
    def root(self):             return self.filter(parent__isnull=True)
    def with_children(self):    return self.prefetch_related("children")
    def with_products(self):    return self.prefetch_related("products")


class CategoryManager(db_models.Manager):
    def get_queryset(self):     return CategoryQuerySet(self.model, using=self._db)
    def with_children(self):    return self.prefetch_related("children")
    def active(self):           return self.get_queryset().active()
    def root_categories(self):  return self.get_queryset().active().root().with_children()


class ProductQuerySet(db_models.QuerySet):
    def active(self):               return self.filter(is_active=True)
    def inactive(self):             return self.filter(is_active=False)
    def by_category(self, cid):     return self.filter(category_id=cid)
    def with_variants(self):        return self.prefetch_related("variants__attributes")
    def with_category(self):        return self.select_related("category")
    def with_stock(self):           return self.prefetch_related("variants__stock_levels__warehouse")
    def with_images(self):          return self.prefetch_related("images")
    def with_videos(self):          return self.prefetch_related("videos")
    def full(self):
         return (
             self.with_category().with_variants().with_stock()
                 .with_images().with_videos()
                 .select_related("brand")
                 .prefetch_related("effects", "variants__lab")
         )

    def in_stock(self):
        return self.filter(
            variants__stock_levels__quantity__gt=db_models.F("variants__stock_levels__reserved")
        ).distinct()

    def out_of_stock(self):
        return self.exclude(
            variants__stock_levels__quantity__gt=db_models.F("variants__stock_levels__reserved")
        ).distinct()

    def price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None: qs = qs.filter(base_price__gte=min_price)
        if max_price is not None: qs = qs.filter(base_price__lte=max_price)
        return qs

    def search(self, query):
        return self.filter(
            db_models.Q(name__icontains=query) |
            db_models.Q(description__icontains=query) |
            db_models.Q(variants__sku__icontains=query)
        ).distinct()


class ProductManager(db_models.Manager):
    def get_queryset(self):     return ProductQuerySet(self.model, using=self._db)
    def active(self):           return self.get_queryset().active()
    def in_stock(self):         return self.get_queryset().active().in_stock()
    def search(self, query):    return self.get_queryset().active().search(query)
    def full(self):              return self.get_queryset().full()

class ProductVariantQuerySet(db_models.QuerySet):
    def active(self):                   return self.filter(is_active=True)
    def for_product(self, product_id):  return self.filter(product_id=product_id)
    def with_attributes(self):          return self.prefetch_related("attributes")
    def with_stock(self):               return self.prefetch_related("stock_levels__warehouse")

    def available(self):
        return self.filter(
            stock_levels__quantity__gt=db_models.F("stock_levels__reserved")
        ).distinct()


class ProductVariantManager(db_models.Manager):
    def get_queryset(self):     return ProductVariantQuerySet(self.model, using=self._db)
    def active(self):           return self.get_queryset().active()
    def available(self):        return self.get_queryset().active().available()


# Integrate into apps/catalog/models.py:
#   Category.objects      = CategoryManager()
#   Product.objects       = ProductManager()
#   ProductVariant.objects= ProductVariantManager()

