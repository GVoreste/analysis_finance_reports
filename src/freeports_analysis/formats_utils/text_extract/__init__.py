"""Module for text block processing and extraction in document analysis.

This module provides functionality for:
- Defining text block types through enumerations
- Matching text against targets using various matching strategies
- Extracting text blocks from PDF documents based on target matches
- Supporting different matching methods (exact, fuzzy, prefix-based)

Key components:
- Matching functions (target_match, target_fuzzy_match, target_prefix_match)
- Decorators for text block type definition (one_txt_blk, EquityBondTextBlockType)
- Standard text extraction functionality through standard_text_extraction decorator
"""

from enum import Enum, auto
import re
import logging
from typing import List, Optional
from freeports_analysis.i18n import _
from freeports_analysis.formats import TextBlock, PdfBlock
from freeports_analysis.consts import Currency
from .match import target_match
from .. import normalize_string, overwrite_if_implemented

logger = logging.getLogger(__name__)


class EquityBondTextBlockType(Enum):
    """Enum representing two type of text blocks in document processing.

    Attributes
    ----------
    BOND_TARGET : enum
        Text block containing target `Bond` row.
    EQUITY_TARGET : enum
        Text block containing target `Equity` row.
    """

    BOND_TARGET = auto()
    EQUITY_TARGET = auto()


def standard_text_extraction_loop(match_func=target_match):
    """Decorator for standard text extraction loop.

    This decorator wrap the function provide in the usual loop that give a simplify
    and higher level context to the decorated `text_extraction` function.
    Specifically it expect that in the metadata of each `PdfBlock` is present
    an indicator of which column it is located graphycally in the main table of the
    pdf page (it suppose that the data was tabular in some way) `table-col`.
    The loop:
    - Take each block and concat the content with the subsequent if
      they are on the same column.
    - Use `match_func` to see if one between the target provided to the
      extraction function match with the content  of the block.
    - If it does it overwrite the list of `PdfBlock` to persist the concatenation
      of the block with is subsequent.
    - Add `company` metadata with the match
    - It create a `TextBlock` addint the metadata provided by the wrapped function.
      The wrapped function take as parameters the block list and the index
      of the matched block. It takes the modified list with merged content
      for block in the same column that matches the target.
    """

    def decorator(f):
        def text_extract(
            pdf_blocks: List[PdfBlock], targets: List[str]
        ) -> List[TextBlock]:
            text_part_list = []
            i = 0
            if len(pdf_blocks) == 0:
                return text_part_list
            while True:
                company_name = False
                split = False
                current_block = pdf_blocks[i]
                next_block = pdf_blocks[i + 1]
                col = current_block.metadata["table-col"]
                next_col = next_block.metadata["table-col"]
                content = current_block.content
                if col == next_col:
                    split = True
                    content += pdf_blocks[i + 1].content
                for target in targets:
                    target_n = normalize_string(target)
                    if target_n != "" and match_func(content, target):
                        company_name = True
                        if company_name and split:
                            pdf_blocks[i].content = content
                            pdf_blocks.pop(i + 1)
                        txt_blk = f(pdf_blocks, i)
                        txt_blk.metadata["company"] = target
                        text_part_list.append(txt_blk)
                        break
                i += 1
                if i >= len(pdf_blocks) - 1:
                    break
            if i == len(pdf_blocks) - 1:
                content = pdf_blocks[-1].content
                for target in targets:
                    target_n = normalize_string(target)
                    if target_n != "" and match_func(content, target):
                        txt_blk = f(pdf_blocks, i)
                        txt_blk.metadata["company"] = target
                        text_part_list.append(txt_blk)
            return text_part_list

        return text_extract

    return decorator


date_regexes = [
    r".*(\d{2}[/-]\d{2}[/-]\d{4}).*",
    r".*(\d{4}[/-]\d{2}[/-]\d{2}).*",
    r".*(\d{2}[/-]\d{2}[/-]\d{2}).*",
]
perc_regexes = [r".*((\d+[\.,]\d+)\s*%).*"]


def standard_text_extraction(
    nominal_quantity_pos: int,
    market_value_pos: int,
    perc_net_assets_pos: int,
    currency: Optional[int | Currency] = None,
    acquisition_cost_pos: Optional[int] = None,
    match_func=target_match,
):
    """Decorator for defining standard text extraction logic
    from PDF blocks based on target matches.

    Parameters
    ----------
    nominal_quantity_pos : int
        Relative position for nominal quantity metadata
    market_value_pos : int
        Relative position for market value metadata
    perc_net_assets_pos : int
        Relative position for percentage of net assets metadata
    currency : Optional[Union[int, Currency]], optional
        Either relative position for currency metadata or Currency enum value, by default None
    acquisition_cost_pos : Optional[int], optional
        Relative position for acquisition cost metadata, by default None
    match_func : callable, optional
        Matching function to compare text against targets, by default target_match

    Returns
    -------
    callable
        A wrapped text extraction function that processes PDF blocks
        and returns matched TextBlock objects
    Notes
    -----
    The decorated function can optionally be specified with
    the purpose of including additional metadata.
    The extraction process:
    1. Normalizes and matches text against targets using the specified match_func
    2. Extracts metadata from surrounding blocks based on extract_positions
    3. Creates TextBlock objects for successful matches
    """

    def wrapper(f):
        @overwrite_if_implemented(f)
        def add_metadata(blks: List[PdfBlock], i: int) -> dict:
            return {}

        @standard_text_extraction_loop(match_func)
        def text_extract(pdf_blocks: List[PdfBlock], i: int) -> TextBlock:
            if nominal_quantity_pos * market_value_pos * perc_net_assets_pos == 0:
                raise ValueError(_("All positions must be non-zero"))
            if (
                nominal_quantity_pos == market_value_pos
                or nominal_quantity_pos == perc_net_assets_pos
                or market_value_pos == perc_net_assets_pos
            ):
                raise ValueError(_("All positions should be different"))

            metadata = {}
            try:
                metadata["subfund"] = pdf_blocks[i].metadata["subfund"]
                metadata["page"] = pdf_blocks[i].metadata["page"]
                metadata["quantity"] = pdf_blocks[i + nominal_quantity_pos].content
                metadata["market value"] = pdf_blocks[i + market_value_pos].content
                metadata["% net assets"] = pdf_blocks[i + perc_net_assets_pos].content
                if isinstance(currency, int):
                    metadata["currency"] = pdf_blocks[i + currency].content
                elif isinstance(currency, Currency):
                    metadata["currency"] = currency.name

                if acquisition_cost_pos is not None:
                    metadata["acquisition cost"] = pdf_blocks[
                        i + acquisition_cost_pos
                    ].content
            except IndexError as e:
                logger.error(str(e))
                return None

            content = pdf_blocks[i].content.replace("\n", "")
            instrument = EquityBondTextBlockType.EQUITY_TARGET
            for reg in perc_regexes:
                interest_rate_match = re.match(reg, content, re.DOTALL)
                if interest_rate_match:
                    instrument = EquityBondTextBlockType.BOND_TARGET
                    metadata["interest rate"] = interest_rate_match[1]
                    break
            for reg in date_regexes:
                date_match = re.match(reg, content, re.DOTALL)
                if date_match:
                    instrument = EquityBondTextBlockType.BOND_TARGET
                    metadata["maturity"] = date_match[1]
                    break

            metadata.update(add_metadata(pdf_blocks, i))
            return TextBlock(instrument, metadata, pdf_blocks[i])

        return text_extract

    return wrapper
