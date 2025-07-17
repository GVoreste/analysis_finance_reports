"""AMUNDI2 format submodule"""

import logging as log
from typing import TypeAlias
from freeports_analysis.formats_utils.pdf_filter import (
    OnePdfBlockType,
    standard_pdf_filtering,
)
from freeports_analysis.formats_utils.text_extract import (
    standard_text_extraction,
    EquityBondTextBlockType,
)
from freeports_analysis.formats_utils.deserialize import standard_deserialization
from freeports_analysis.formats_utils.pdf_filter.pdf_parts.position import YRange
from freeports_analysis.consts import Currency

logger = log.getLogger(__name__)


PdfBlockType: TypeAlias = OnePdfBlockType
TextBlockType: TypeAlias = EquityBondTextBlockType


@standard_pdf_filtering(
    header_txt="Titolo",
    header_font="TrebuchetMS-Bold",
    subfund_height=YRange(None, 60),
    subfund_font="Arial-BoldItalicMT",
    body_font="TrebuchetMS",
    y_range=(None, None),
    algorithm_flags=[False, False, True, False],
    tolerance=5.0,
)
def pdf_filter(xml_root) -> dict:
    pass


@standard_text_extraction(
    nominal_quantity_pos=+1,
    market_value_pos=+4,
    perc_net_assets_pos=+5,
    currency=Currency.EUR,
    acquisition_cost_pos=None,
)
def text_extract(pdf_blocks, targets):
    pass


@standard_deserialization(
    cost_and_value_interpret_int=False, quantity_interpret_float=True
)
def deserialize(text_block, targets):
    pass
