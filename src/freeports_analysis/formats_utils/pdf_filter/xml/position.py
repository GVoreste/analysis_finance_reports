"""PDF block element utilities for spatial analysis and manipulation.

This module provides functions for working with PDF block elements (represented as lxml.etree.Element objects)
that contain bounding box information. It includes utilities for checking spatial relationships,
extracting coordinates, and calculating dimensions of PDF content blocks.
"""

from typing import Optional, Tuple
from lxml import etree


def is_contained(
    blk: etree.Element,
    x_range: Optional[Tuple[float, float]] = None,
    y_range: Optional[Tuple[float, float]] = None,
) -> bool:
    """Check if a block's bounding box is fully contained within specified ranges.

    Parameters
    ----------
    blk : etree.Element
        XML element representing a PDF block
    x_range : Optional[Tuple[float, float]], optional
        Horizontal range (min_x, max_x)
    y_range : Optional[Tuple[float, float]], optional
        Vertical range (min_y, max_y)

    Returns
    -------
    bool
        True if entire bbox is within ranges, False otherwise
    """
    bounds = get_bounds(blk)

    if x_range is not None:
        l = x_range[0]
        r = x_range[1]
        if l is not None and bounds[0][0] < l:
            return False
        if r is not None and bounds[0][1] > r:
            return False

    if y_range is not None:
        t = y_range[0]
        b = y_range[1]
        if t is not None and bounds[1][0] < t:
            return False
        if b is not None and bounds[1][1] > b:
            return False

    return True


def get_bounds(blk: etree.Element) -> list | None:
    """Get the horizontal and vertical bounds of a block's bounding box.

    Parameters
    ----------
    blk : etree.Element
        XML element representing a PDF block, expected to contain a 'bbox' attribute.

    Returns
    -------
    list of tuple or None
        A list containing two tuples representing horizontal (x0, x1) and vertical (y0, y1) bounds.
        Returns None if no 'bbox' attribute is found.
    """
    bbox = blk.xpath(".//@bbox")
    if not bbox:
        return None

    coords = [float(c) for c in bbox[0].split()]
    coords = ((coords[0], coords[2]), (coords[1], coords[3]))
    return coords


def get_position(blk: etree.Element, mean: bool) -> list | None:
    """Return the coordinates or center of a bounding box from a PDF block element.
    Parameters
    ----------
    blk : etree.Element
        XML element representing the PDF block, expected to contain a 'bbox' attribute.
    mean : bool
        If True, return the center point (x, y) of the bounding box.
        If False, return the full bounding box coordinates (x0, y0, x1, y1).
    Returns
    -------
    list of float or None
        A list of float values representing either the full bounding box or its center.
        Returns None if no 'bbox' attribute is found.
    """

    bbox = blk.xpath(".//@bbox")
    if not bbox:
        return None

    coords = [float(c) for c in bbox[0].split()]  # x0, y0, x1, y1

    if mean:
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2
        coords = (x_center, y_center)
    else:
        coords = (
            ((coords[0], coords[1]), (coords[0], coords[3])),
            ((coords[2], coords[1]), (coords[2], coords[3])),
        )

    return coords


def get_size(blk: etree.Element) -> Tuple[float, float]:
    """Calculate the width and height of a block's bounding box.

    Parameters
    ----------
    blk : etree.Element
        XML element representing a PDF block with a 'bbox' attribute

    Returns
    -------
    Tuple[float, float]
        A tuple containing (width, height) of the bounding box
    """
    x_bounds, y_bounds = get_bounds(blk)
    return (x_bounds[1] - x_bounds[0], y_bounds[1] - y_bounds[0])


def is_positioned(
    blk: etree.Element,
    x_range: Optional[Tuple[float, float]] = None,
    y_range: Optional[Tuple[float, float]] = None,
) -> bool:
    """Check if a block is positioned within specified x and/or y ranges.
    Parameters
    ----------
    blk : etree.Element
        XML element representing a PDF block
    x_range : Optional[Tuple[float, float]], optional
        Minimum and maximum x-coordinate values (left, right)
    y_range : Optional[Tuple[float, float]], optional
        Minimum and maximum y-coordinate values (bottom, top)
    Returns
    -------
    bool
        True if block's coordinates are within specified ranges, False otherwise
    """
    coords = get_position(blk, True)
    if x_range is not None:
        if not x_range[0] <= coords[0] <= x_range[1]:
            return False

    if y_range is not None:
        if not y_range[0] <= coords[1] <= y_range[1]:
            return False

    return True


def get_lines_contained(
    blk: etree.Element,
    x_range: Optional[Tuple[float, float]] = None,
    y_range: Optional[Tuple[float, float]] = None,
):
    lines = blk.findall(".//line")
    return [ln for ln in lines if is_contained(ln, x_range, y_range)]
