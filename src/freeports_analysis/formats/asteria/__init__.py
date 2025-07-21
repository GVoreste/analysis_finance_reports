"""ASTERIA submodule"""

from freeports_analysis.formats_utils.pdf_filter import standard_pdf_filtering, YRange
from freeports_analysis.formats_utils.text_extract import standard_text_extraction
from freeports_analysis.formats_utils.deserialize import standard_deserialization


@standard_pdf_filtering(
    header_txt="Transferable securities admitted to an official stock",
    header_font="CenturyGothic-Bold",
    subfund_height=YRange(None, 87),
    subfund_font="CenturyGothic-Bold",
    body_font="CenturyGothic",
    y_range=(None, 810),
)
def pdf_filter(xml_root):
    raise NotImplementedError


@standard_text_extraction(
    currency=+2,
    nominal_quantity_pos=+1,
    market_value_pos=+4,
    perc_net_assets_pos=+5,
    acquisition_cost_pos=+3,
)
def text_extract(pdf_blks, targets):
    raise NotImplementedError


@standard_deserialization(True)
def deserialize(txt_blks, targets):
    raise NotImplementedError
