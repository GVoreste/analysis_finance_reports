"""EURIZON_IT format submodule"""

from freeports_analysis.consts import Currency
from freeports_analysis.formats_utils.pdf_filter import standard_pdf_filtering, YRange
from freeports_analysis.formats_utils.text_extract import standard_text_extraction
from freeports_analysis.formats_utils.deserialize import standard_deserialization


@standard_pdf_filtering(
    header_txt="Elenco",
    header_font="TrebuchetMS,Bold",
    subfund_height=YRange(793, 803),
    subfund_font="TrebuchetMS,Italic",
    body_font="TrebuchetMS",
    y_range=None,
)
def pdf_filter(xml_root) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=+1,
    market_value_pos=+2,
    perc_net_assets_pos=+4,
    currency=Currency.EUR,
)
def text_extract(pdf_blocks, targets):
    raise NotImplementedError


@standard_deserialization()
def deserialize(text_block, targets):
    raise NotImplementedError
