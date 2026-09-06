from decimal import Decimal

from apps.catalog_peptides.management.commands.import_peptide_catalog import (
    infer_profile,
    parse_catalog_page,
)


def test_parse_woocommerce_catalog_cards():
    html = """
    <ul class="products"><li class="product">
      <a href="/product/bpc-157/"><h2 class="woocommerce-loop-product__title">BPC-157 10mg</h2></a>
      <div class="product-categories"><a>Research Peptides</a></div>
      <span class="price"><del>$89.00</del><ins>$69.00</ins></span>
      <img data-lazy-src="/media/bpc.jpg" />
    </li></ul>
    """
    products = parse_catalog_page(html, "https://catalog.example/shop/")
    assert len(products) == 1
    assert products[0].name == "BPC-157 10mg"
    assert products[0].price == Decimal("69.00")
    assert products[0].compare_at_price == Decimal("89.00")
    assert products[0].image_url == "https://catalog.example/media/bpc.jpg"


def test_infer_profile_from_product_name():
    assert infer_profile("Example 5mg Blend") == {
        "concentration": "5mg",
        "form": "Lyophilized blend",
        "storage_requirements": "Store according to the supplier documentation. Research use only.",
    }
