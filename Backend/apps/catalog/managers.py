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
    def root_categories(self):
        # No .with_children() here: CategoryListView always follows this
        # with attach_full_tree(), which fetches (and stamps) the whole
        # active tree in one query and ignores any prefetch on `objs`.
        # Keeping with_children() here just bought a second, wasted query.
        return self.get_queryset().active().root()

    def attach_full_tree(self, objs):
        """
        CategorySerializer.get_children() recurses through the category
        tree, and `with_children()` only prefetches one level deep — so
        every level below that was issuing one query per node (N+1,
        scaling with tree size, not just depth).

        This loads every active category in a single query, links each
        node to its children in memory, and stamps that onto `objs` (and
        all of their descendants) as `_prefetched_children`, so the
        recursive serializer never touches the DB again.
        """
        objs = list(objs)
        by_parent = {}
        for cat in self.get_queryset().active().order_by("name", "id"):
            by_parent.setdefault(cat.parent_id, []).append(cat)

        def link(cat):
            children = by_parent.get(cat.id, [])
            cat._prefetched_children = children
            for child in children:
                link(child)

        for obj in objs:
            link(obj)
        return objs


class ProductQuerySet(db_models.QuerySet):
    def active(self):               return self.filter(is_active=True)
    def inactive(self):             return self.filter(is_active=False)
    def by_category(self, cid):     return self.filter(category_id=cid)
    def with_variants(self):
        return self.prefetch_related("variants__attributes", "variants__images", "variants__videos")
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

    def with_coa(self):
        """Variants that carry a real, on-file Lab record with a
        certificate of analysis link — i.e. a verifiable lab-testing
        claim, not just a badge graphic. Backs the public Lab Results
        index page."""
        return self.filter(product__is_active=True, lab__isnull=False).exclude(lab__coa_url="")


class ProductVariantManager(db_models.Manager):
    def get_queryset(self):     return ProductVariantQuerySet(self.model, using=self._db)
    def active(self):           return self.get_queryset().active()
    def available(self):        return self.get_queryset().active().available()
    def with_coa(self):         return self.get_queryset().active().with_coa()

