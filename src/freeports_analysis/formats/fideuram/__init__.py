"""FIDEURAM format submodule"""

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
    header_txt="Country",
    header_font="Arial",
    subfund_height=YRange(None, 82),
    subfund_font="Arial-Bold",
    body_font="Arial",
    y_range=(103, 749),
    deselection_list=[
        ("SHARES, WARRANTS, RIGHTS", "Arial"),
        (
            "TRANSFERABLE SECURITIES AND MONEY MARKET INSTRUMENTS ADMITTED TO AN OFFICIAL",
            "Arial",
        ),
        ("EXCHANGE LISTING OR DEALT IN ON OTHER REGULATED MARKETS", "Arial"),
        ("BONDS AND ASSIMILATED STRUCTURED PRODUCTS", "Arial"),
        ("INVESTMENT FUNDS", "Arial"),
    ],
)
def pdf_filter(xml_root) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=-1,
    market_value_pos=+1,
    perc_net_assets_pos=+2,
    currency=-2,
    acquisition_cost_pos=None,
)
def text_extract(pdf_blocks, targets):
    raise NotImplementedError


@standard_deserialization()
def deserialize(text_block, targets):
    raise NotImplementedError
