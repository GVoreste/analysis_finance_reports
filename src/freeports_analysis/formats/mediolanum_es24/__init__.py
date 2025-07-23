from enum import Enum, auto
from typing import List, TypeAlias
import re
from lxml import etree
from freeports_analysis.consts import Equity, Bond, Currency
from freeports_analysis.formats_utils.pdf_filter import (
    standard_pdf_filtering,
    OnePdfBlockType,
)
from freeports_analysis.formats_utils.pdf_filter.pdf_parts import YRange
from freeports_analysis.formats_utils.text_extract import (
    standard_text_extraction,
    EquityBondTextBlockType,
)
from freeports_analysis.formats_utils.deserialize import standard_deserialization
from .. import PdfBlock, TextBlock


@standard_pdf_filtering(
    header_font="TimesNewRomanPSMT",
    header_txt="n de la cartera",
    subfund_height=YRange(60, 77),
    subfund_font="TimesNewRomanPSMT",
    body_font="TimesNewRomanPSMT",
)
def pdf_filter(xml_root: etree.Element) -> dict:
    raise NotImplementedError


@standard_text_extraction(
    nominal_quantity_pos=1,
    market_value_pos=4,
    perc_net_assets_pos=5,
    acquisition_cost_pos=3,
    currency=2,
)
def text_extract(pdf_blocks: List[PdfBlock], targets: List[str]) -> List[TextBlock]:
    raise NotImplementedError


@standard_deserialization()
def deserialize(txt_blk: TextBlock, targets: List[str]):
    raise NotImplementedError


PdfBlockType: TypeAlias = OnePdfBlockType
TextBlockType: TypeAlias = EquityBondTextBlockType
