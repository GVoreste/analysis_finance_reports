"""EURIZON format submodule"""

import logging as log
from typing import TypeAlias
from freeports_analysis.formats_utils.pdf_filter import (
    OnePdfBlockType,
    standard_pdf_filtering,
    YRange,
)
from freeports_analysis.formats_utils.text_extract import (
    standard_text_extraction,
    EquityBondTextBlockType,
)
from freeports_analysis.formats_utils.deserialize import standard_deserialization

logger = log.getLogger(__name__)


PdfBlockType: TypeAlias = OnePdfBlockType
TextBlockType: TypeAlias = EquityBondTextBlockType


@standard_pdf_filtering(
    header_txt="PORTFOLIO AS AT",
    header_font="Frutiger-Black",
    subfund_height=YRange(65, 85),
    subfund_font="Frutiger-Black",
    body_font="Frutiger-Light",
    y_range=(160, 765),
)
def pdf_filter(xml_root) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=-1,
    market_value_pos=+3,
    perc_net_assets_pos=+4,
    currency=+1,
    acquisition_cost_pos=+2,
)
def text_extract(pdf_blocks, targets):
    raise NotImplementedError


@standard_deserialization(cost_and_value_interpret_int=False)
def deserialize(text_block, targets):
    raise NotImplementedError
