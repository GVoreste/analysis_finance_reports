"""ASTERIA 2023 submodule"""

from freeports_analysis.formats_utils.pdf_filter import standard_pdf_filtering, YRange
from freeports_analysis.formats_utils.text_extract import standard_text_extraction
from freeports_analysis.formats_utils.deserialize import standard_deserialization


@standard_pdf_filtering(
    header_txt="Number of Shares/",
    header_font="CenturyGothic-Bold",
    subfund_height=YRange(80, 95),
    subfund_font="CenturyGothic-Bold",
    body_font="CenturyGothic",
    y_range=None,
)
def pdf_filter(xml_root) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=+1,
    market_value_pos=+4,
    perc_net_assets_pos=+5,
    currency=+2,
    acquisition_cost_pos=+3,
)
def text_extract(pdf_blocks, targets):
    raise NotImplementedError


@standard_deserialization()
def deserialize(text_block, targets):
    raise NotImplementedError
