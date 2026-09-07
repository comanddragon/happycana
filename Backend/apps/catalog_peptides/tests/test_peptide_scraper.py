import importlib.util
from decimal import Decimal
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / ".scripts" / "peptides" / "products" / "scrape_products.py"
SPEC = importlib.util.spec_from_file_location("peptide_scraper", SCRIPT)
scraper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scraper)


def test_detail_parser_prefers_product_image_over_sitewide_open_graph_image():
    product = scraper.ScrapedProduct(
        source_url="https://peptidesdirect.com/product/VESUG",
        name="Vesugen",
        price=Decimal(39),
        image_url="https://peptidesdirect.com/images/og-share-wide.png",
    )
    html = """
        <html><head>
          <meta property="og:image" content="/images/og-share-wide.png">
        </head><body>
          <img alt="PeptidesDirect logo" src="/images/logo.png">
          <img alt="Vesugen 20mg" src="/images/products/vesugen-20mg.jpg">
        </body></html>
    """

    scraper.parse_product_detail(html, product)

    assert product.image_url == "https://peptidesdirect.com/images/products/vesugen-20mg.jpg"


def test_detail_parser_does_not_replace_missing_product_media_with_sitewide_artwork():
    product = scraper.ScrapedProduct(
        source_url="https://peptidesdirect.com/product/UNKNOWN",
        name="Unknown",
    )
    html = '<meta property="og:image" content="/images/og-share-wide.png">'

    scraper.parse_product_detail(html, product)

    assert product.image_url == ""
