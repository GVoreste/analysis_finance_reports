"""Utilities for writing `pdf_filter` functions.

This module provides decorators and utilities for filtering and processing PDF content
based on XML elements, fonts, and positional data.
"""

from typing import List, Optional, Tuple, TypeAlias, Callable
from enum import Enum, auto
from lxml import etree
from freeports_analysis.formats import PdfBlock, ExpectedPdfBlockNotFound, TextBlock
from freeports_analysis.i18n import _
from .xml.font import get_lines_with_font, is_present_txt_font, get_lines_with_txt_font
from .select_position import select_inside, get_table_positions, TablePosAlgorithm
from .pdf_parts.position import YRange
from .pdf_parts.font import Font
from .pdf_parts import ExtractedPdfLine
from .select_font import deselect_txt_font
from .xml.position import get_bounds
from .. import overwrite_if_implemented

UpdateMetadataFunc: TypeAlias = Callable[[etree.Element], dict]
FilterCondition: TypeAlias = Callable[[etree.Element], bool]
PdfFilterFunc: TypeAlias = Callable[[etree.Element], List[TextBlock]]


class OnePdfBlockType(Enum):
    """Enum representing types of PDF blocks in document processing.

    Attributes
    ----------
    RELEVANT_BLOCK : enum
        PDF block containing relevant information to extract.
    """

    RELEVANT_BLOCK = auto()


def filter_page_if(
    condition: FilterCondition,
) -> Callable[[PdfFilterFunc], PdfFilterFunc]:
    """Decorator factory for conditionally applying a PDF filter based on a predicate.

    Creates a decorator that will only execute the wrapped PDF filter function if the
    specified condition evaluates to True for the given XML root element.

    Parameters
    ----------
    condition : Callable[[etree.Element], bool]
        A predicate function that determines whether the filter should be applied.

    Returns
    -------
    Callable[[PdfFilterFunc], PdfFilterFunc]
        A decorator that conditionally applies the PDF filter.
    """

    def wrapper(pdf_filter: PdfFilterFunc) -> PdfFilterFunc:
        def conditionated_pdf_filter(xml_root: etree.Element) -> List[PdfBlock]:
            parts = []
            if condition(xml_root):
                parts = pdf_filter(xml_root)
            return parts

        return conditionated_pdf_filter

    return wrapper


def standard_extraction_subfund(
    subfund_height: YRange,
    subfund_font: str,
) -> Callable[[UpdateMetadataFunc], UpdateMetadataFunc]:
    """Decorator for extracting subfund text and updating metadata.

    Parameters
    ----------
    subfund_height : YRange
        The vertical range in which the subfund text is expected.
    subfund_font : str
        The font used by the subfund text.

    Returns
    -------
    Callable[[UpdateMetadataFunc], UpdateMetadataFunc]
        A decorator that updates metadata with the extracted subfund text.
    """

    def decorator(old_page_metadata):
        def new_page_metadata(xml_root: etree.Element) -> List[PdfBlock]:
            lines_with_font = get_lines_with_font(xml_root, subfund_font)
            lines = [ExtractedPdfLine(blk) for blk in lines_with_font]
            top_lines = select_inside(lines, subfund_height)
            subfund = None
            if len(top_lines) > 0:
                subfund = top_lines[0].xml_blk.xpath(".//@text")[0]
            if subfund is None:
                raise ExpectedPdfBlockNotFound(
                    _("subfund block on top of page not found")
                )
            metadata = old_page_metadata(xml_root)
            metadata["subfund"] = subfund
            return metadata

        return new_page_metadata

    return decorator


def standard_pdf_filtering(
    header_txt: str,
    header_font: Font,
    subfund_height: YRange,
    subfund_font: Font,
    body_font: str,
    y_range: Optional[
        Tuple[Optional[float | Tuple[str, str]], Optional[float | Tuple[str, str]]]
    ] = None,
    deselection_list: Optional[Tuple[str, Font]] = None,
    algorithm_flags: List = [False, False, False, False],
    tolerance: float = 0.0,
) -> Callable[[PdfFilterFunc], PdfFilterFunc]:
    """Decorator factory for creating PDF filters with standardized processing.

    Creates a filter that:
    1. Processes pages containing the specified header text in the specified header font.
    2. Extracts lines with the specified body font as relevant blocks.
    3. Extracts subfund text within a specified range or height.
    4. Allows customization of page metadata and block types.

    Parameters
    ----------
    header_txt : str
        The text that must be present in the header to process the page.
    header_font : Font
        The font used by the header text.
    subfund_height : YRange
        The vertical range or height for subfund extraction.
    subfund_font : Font
        The font used by the subfund text.
    body_font : str
        The font used by the body text to extract as relevant blocks.
    y_range : Optional[Tuple[Optional[float | Tuple[str, str]], Optional[float | Tuple[str, str]]]
        The vertical range for filtering lines, by default None.
    deselection_list : Optional[Tuple[str, Font]], optional
        A list of text and font pairs to exclude from extraction, by default None.

    Returns
    -------
    Callable[[PdfFilterFunc], PdfFilterFunc]
        A decorator that applies the standardized PDF filter.
    """

    def decorator(f):
        @standard_extraction_subfund(subfund_height, subfund_font)
        @overwrite_if_implemented(f)
        def page_metadata(_: etree.Element) -> dict:
            return {}

        @filter_page_if(lambda x: is_present_txt_font(x, header_txt, header_font))
        def pdf_filter(xml_root: etree.Element) -> List[PdfBlock]:
            metadata = page_metadata(xml_root)
            rows = get_lines_with_font(xml_root, body_font)
            lines = [ExtractedPdfLine(r) for r in rows]
            y_range_numeric_top = None
            y_range_numeric_btm = None

            if deselection_list is not None:
                lines = deselect_txt_font(
                    deselection_list=deselection_list, lines=lines
                )

            if y_range is not None:
                if isinstance(y_range[0], tuple):
                    txt, font = y_range[0]
                    top_limit_blk = get_lines_with_txt_font(xml_root, txt, font)
                    if top_limit_blk is not None:
                        y_range_numeric_top = get_bounds(top_limit_blk)[1][1]
                else:
                    y_range_numeric_top = y_range[0]
                if isinstance(y_range[1], tuple):
                    txt, font = y_range[1]
                    btm_limit_blk = get_lines_with_txt_font(xml_root, txt, font)
                    if btm_limit_blk is not None:
                        y_range_numeric_btm = get_bounds(btm_limit_blk)[1][0]
                else:
                    y_range_numeric_btm = y_range[1]
            table_rows = select_inside(
                lines, YRange(y_range_numeric_top, y_range_numeric_btm)
            )

            all_flags = [
                TablePosAlgorithm.ROW,
                TablePosAlgorithm.BIG_RULE,
                TablePosAlgorithm.RULER_AREA,
                TablePosAlgorithm.TEST_POS,
            ]

            algo = TablePosAlgorithm(0)  # valore vuoto (nessun flag attivo)
            for flag, enabled in zip(all_flags, algorithm_flags):
                if enabled:
                    algo |= flag

            table_positions = get_table_positions(
                table_rows, algorithm_flags=algo, tolerance=tolerance
            )
            return [
                PdfBlock(
                    OnePdfBlockType.RELEVANT_BLOCK,
                    {**metadata, "table-col": table_positions[i]},
                    table_row.xml_blk,
                )
                for i, table_row in enumerate(table_rows)
            ]

        return pdf_filter

    return decorator
