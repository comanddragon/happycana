import runpy
from decimal import Decimal
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / ".scripts" / "hash" / "products" / "scrape_products.py"
SCRAPER = runpy.run_path(SCRIPT)


def test_money_uses_woocommerce_minor_unit():
    assert SCRAPER["money"]({"price": "1299", "currency_minor_unit": 2}) == "12.99"


def test_potency_extracts_named_cannabinoids():
    assert SCRAPER["potency"]("Pressed hash — 27.5% THCA and 2% CBD") == {
        "thc_percent": "",
        "thca_percent": "27.5",
        "cbd_percent": "2",
    }


def test_parse_variations_reads_public_woocommerce_payload():
    payload = """[{&quot;attributes&quot;:{&quot;attribute_quantity&quot;:&quot;25g&quot;},
        &quot;display_price&quot;:170,&quot;display_regular_price&quot;:200,
        &quot;variation_id&quot;:9520,&quot;variation_is_active&quot;:true,
        &quot;is_in_stock&quot;:true,&quot;sku&quot;:&quot;&quot;,&quot;image&quot;:{}}]"""
    page = f'<form class="variations_form" data-product_variations="{payload}"></form>'
    rows = SCRAPER["parse_variations"](page, {"id": 9518})
    assert rows[0]["id"] == "frozenhashish:9520"
    assert Decimal(rows[0]["price"]) == Decimal(170)
    assert rows[0]["weight_value"] == "25"
    assert rows[0]["weight_unit"] == "grams"
