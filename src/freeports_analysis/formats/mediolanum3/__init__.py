"""MEDIOLANUM3 submodule"""

from freeports_analysis.formats_utils.pdf_filter import standard_pdf_filtering, YRange
from freeports_analysis.formats_utils.text_extract import standard_text_extraction
from freeports_analysis.formats_utils.deserialize import standard_deserialization
from freeports_analysis.formats_utils.text_extract.match import (
    target_fuzzy_match,
    target_prefix_match,
)


@standard_pdf_filtering(
    header_txt="Descrizione",
    header_font="TT5D22o00",
    subfund_height=YRange(47, 62),
    subfund_font="TT5CC2o00",
    body_font="TT5D42o00",
    y_range=None,
    algorithm_flags=[False, False, False, False],
    tolerance=0,
)
def pdf_filter(xml_root) -> dict:
    pass


@standard_text_extraction(
    nominal_quantity_pos=+1,
    market_value_pos=+4,
    perc_net_assets_pos=+5,
    currency=+2,
    acquisition_cost_pos=+3,
    match_func=lambda x, y: target_fuzzy_match(x, y, 0.8)
    and target_prefix_match(x, y, 0.3),
)
def text_extract(pdf_blocks, targets):
    pass


@standard_deserialization()
def deserialize(text_block, targets):
    pass
