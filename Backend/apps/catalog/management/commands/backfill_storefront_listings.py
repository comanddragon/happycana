from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import Listing, Product
from apps.storefronts.models import Storefront


class Command(BaseCommand):
    help = "Create missing storefront listings from active canonical products. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument("storefront", help="Storefront slug, for example: dispensary")
        parser.add_argument(
            "--all-kinds",
            action="store_true",
            help="Include every product kind instead of matching the storefront kind.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            storefront = Storefront.objects.get(slug=options["storefront"], is_active=True)
        except Storefront.DoesNotExist as exc:
            raise CommandError("Active storefront not found.") from exc

        products = Product.objects.filter(is_active=True).prefetch_related("categories")
        product_kind_by_storefront = {
            Storefront.Kind.DISPENSARY: Product.Kind.CANNABIS,
            Storefront.Kind.HASH: Product.Kind.CANNABIS,
            Storefront.Kind.PEPTIDES: Product.Kind.PEPTIDE,
            Storefront.Kind.FOOTWEAR: Product.Kind.FOOTWEAR,
        }
        product_kind = product_kind_by_storefront.get(storefront.kind)
        if not options["all_kinds"] and product_kind:
            products = products.filter(kind=product_kind)

        existing_product_ids = set(
            Listing.objects.filter(storefront=storefront).values_list("product_id", flat=True)
        )
        products = [product for product in products if product.id not in existing_product_ids]

        listings = [
            Listing(
                storefront=storefront,
                product=product,
                slug=product.slug,
                is_active=True,
                is_featured=product.is_featured,
                meta_title=product.meta_title,
                meta_description=product.meta_description,
            )
            for product in products
        ]
        Listing.objects.bulk_create(listings, batch_size=500)

        category_links = [
            Listing.categories.through(listing_id=listing.id, category_id=category.id)
            for listing, product in zip(listings, products)
            for category in product.categories.all()
        ]
        Listing.categories.through.objects.bulk_create(
            category_links, batch_size=1000, ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(listings)} listing(s) for storefront '{storefront.slug}'."
            )
        )
