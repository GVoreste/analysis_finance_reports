"""Low level utilities for handling typographic related aspects of the xml tree."""

from typing import List, Union
from lxml import etree


def is_present_txt_font(blk: etree.Element, txt: str, font: str) -> bool:
    """Return if a certain pdf block with a specific text and font is present in the tree

    Parameters
    ----------
    blk : etree.Element
        tree to search in
    txt : str
        text to search
    font : str
        font to search

    Returns
    -------
    bool
        boolean describing if the block is present or not
    """
    relevant_part = get_lines_with_txt_font(blk, txt, font, all_elem=True)
    return len(relevant_part) > 0


def get_lines_with_txt_font(
    blk: etree.Element, txt: str, font: str, all_elem: bool = False
) -> List[etree.Element] | etree.Element:
    """Get lines with a certain txt and font

    Parameters
    ----------
    blk : etree.Element
        xml tree structure
    txt : str
        text to search for
    font : str
        font to search for
    all_elem : bool, optional
        if `True` return a list with all matches, if `False` just the first
        as a scalar element

    Returns
    -------
    List[etree.Element] | etree.Element
        matching lines
    """
    blks = blk.xpath(
        f"./descendant-or-self::line[contains(@text,'{txt}') and font[@name='{font}']]"
    )
    return blks if all_elem else blks[0] if len(blks) > 0 else None


def get_lines_with_font(
    blk: etree.Element, font: Union[str, List[str]]
) -> List[etree.Element]:
    """Return all the lines with certain font(s) in a tree

    Parameters
    ----------
    blk : etree.Element
        Tree from which to extract lines
    font : Union[str, List[str]]
        Font or list of fonts to extract

    Returns
    -------
    List[etree.Element]
        List of relevant lines
    """
    if isinstance(font, str):
        fonts = [font]
    else:
        fonts = font

    # Costruisci la condizione XPath per ogni font
    font_conditions = " or ".join([f"font[@name='{f}']" for f in fonts])
    xpath_query = f"./descendant-or-self::line[{font_conditions}]"

    return blk.xpath(xpath_query)
