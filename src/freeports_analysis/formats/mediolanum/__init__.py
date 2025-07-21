"""MEDIOLANUM format submodule"""

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
from freeports_analysis.formats_utils.text_extract.match import (
    target_fuzzy_match,
    target_prefix_match,
)
from freeports_analysis.consts import Currency


logger = log.getLogger(__name__)


PdfBlockType: TypeAlias = OnePdfBlockType
TextBlockType: TypeAlias = EquityBondTextBlockType


@standard_pdf_filtering(
    header_txt="Relazione di gestione al 30 dicembre 2024",
    header_font="Helvetica",
    subfund_height=YRange(None, 76),
    subfund_font="Helvetica",
    body_font="Helvetica",
    y_range=(83, None),
)
def pdf_filter(xml_root) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=+1,
    market_value_pos=+2,
    perc_net_assets_pos=+3,
    currency=Currency.EUR,
    acquisition_cost_pos=None,
    match_func=lambda x, y: target_fuzzy_match(x, y, 0.65)
    and target_prefix_match(x, y, 0.3),
)
def text_extract(pdf_blocks, targets):
    raise NotImplementedError


@standard_deserialization()
def deserialize(text_block, targets):
    raise NotImplementedError
