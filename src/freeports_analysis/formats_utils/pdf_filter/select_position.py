"""Utilities for selecting or deselecting lines or getting infos based of geometrical information"""

from typing import List

from .pdf_parts import ExtractedPdfLine
from .pdf_parts.position import XRange, YRange


def select_inside(
    lines: List[ExtractedPdfLine], bounds: XRange | YRange
) -> List[ExtractedPdfLine]:
    """Select only lines inside a range

    Parameters
    ----------
    lines : List[ExtractedPdfLine]
        lines to filter
    bounds : XRange | YRange
        area to filter from

    Returns
    -------
    List[ExtractedPdfLine]
        lines inside `bounds`
    """
    coord = 0 if isinstance(bounds, XRange) else 1
    return [line for line in lines if line.c[coord] in bounds]


def select_outside(
    lines: List[ExtractedPdfLine], bounds: XRange | YRange
) -> List[ExtractedPdfLine]:
    """Select only lines outside a range

    Parameters
    ----------
    lines : List[ExtractedPdfLine]
        lines to filter
    bounds : XRange | YRange
        area to filter from

    Returns
    -------
    List[ExtractedPdfLine]
        lines outside `bounds`
    """
    coord = 0 if isinstance(bounds, XRange) else 1
    return [line for line in lines if line.c[coord] not in bounds]


def _area_position_algorithm(
    areas,
    indexes,
    ruler_geometry,
    curr_idx,
    mode_flags,
    font_sizes,
    font_tol_ratio=0.5,
):
    return_columns, use_ruler_pos, use_font_sizes = mode_flags
    ruler_pos, ruler_bounds = ruler_geometry
    font_tolerances = font_tol_ratio * font_sizes

    for i, area in enumerate(areas):
        if indexes[i] is not None:
            continue

        if return_columns:
            test_pos = area.c[0]
            test_bounds = area.x_bounds
            default_tolerance = area.width * font_tol_ratio
        else:
            test_pos = area.c[1]
            test_bounds = area.y_bounds
            default_tolerance = area.height * font_tol_ratio

        tolerance = font_tolerances[i] if use_font_sizes else default_tolerance

        if use_ruler_pos:
            match_pos = ruler_pos
            min_bound, max_bound = test_bounds
        else:
            match_pos = test_pos
            min_bound, max_bound = ruler_bounds

        if (min_bound - tolerance) <= match_pos <= (max_bound + tolerance):
            indexes[i] = curr_idx

    return indexes


def _area_intersection_algorithm(
    areas, indexes, ruler_geometry, curr_idx, mode_flags, font_sizes, font_tol_ratio=0.5
):
    return_columns, _, use_font_sizes = mode_flags
    _, ruler_bounds = ruler_geometry
    font_tolerances = font_tol_ratio * font_sizes

    for i, area in enumerate(areas):
        if indexes[i] is not None:
            continue

        if return_columns:
            test_bounds = area.x_bounds
            default_tolerance = area.width * font_tol_ratio
        else:
            test_bounds = area.y_bounds
            default_tolerance = area.height * font_tol_ratio

        tolerance = font_tolerances[i] if use_font_sizes else default_tolerance

        min_bound_t, max_bound_t = test_bounds
        min_bound_r, max_bound_r = ruler_bounds

        if (min_bound_r - tolerance) <= max_bound_t <= (max_bound_r + tolerance) or (
            min_bound_r - tolerance
        ) <= min_bound_t <= (max_bound_r + tolerance):
            indexes[i] = curr_idx

    return indexes


def _algorithm(
    areas,
    indexes,
    ruler_geometry,
    curr_idx,
    mode_flags,
    logic,
    font_sizes,
    font_tol_ratio=0.5,
):
    if logic == 1:
        return _area_intersection_algorithm(
            areas,
            indexes,
            ruler_geometry,
            curr_idx,
            mode_flags,
            font_sizes,
            font_tol_ratio=0.5,
        )
    elif logic == 2:
        return _area_position_algorithm(
            areas,
            indexes,
            ruler_geometry,
            curr_idx,
            mode_flags,
            font_sizes,
            font_tol_ratio=0.5,
        )


def get_table_positions(
    lines: List[ExtractedPdfLine],
    return_columns: bool = True,
    small_rule: bool = True,
    use_ruler_pos: bool = True,
    use_font_sizes: bool = True,
    logic: int = 1,
) -> List[int]:
    """Compute either row or column indexes for areas in a tabular layout.

    Parameters
    ----------
    return_columns : bool
        Whether to return column indexes (True) or row indexes (False)
    areas : list of Area
        List of areas representing table cells
    small_rule : bool
        Whether to use smallest (True) or largest (False) dimension for rulers
    use_ruler_pos : bool
        Whether to use ruler position (True) or bounds (False) for classification

    Returns
    -------
    list of int
        A list of indexes corresponding to each area
    """
    # Initialize indexes
    indexes = [None for _ in lines]
    areas = [line.geometry for line in lines]
    font_sizes = [line.text_size for line in lines]
    rulers = []

    # Choose min/max function based on small_rule
    choose = min if small_rule else max

    while None in indexes:
        curr_idx = len(rulers)
        # Get unindexed areas
        unindexed = [
            (i, area.width if return_columns else area.height)
            for i, area in enumerate(areas)
            if indexes[i] is None
        ]

        # Select ruler for this axis
        ruler_idx, _ = choose(unindexed, key=lambda x: x[1])
        ruler_area = areas[ruler_idx]

        # Get ruler bounds and position
        ruler_bounds = ruler_area.x_bounds if return_columns else ruler_area.y_bounds
        ruler_pos = ruler_area.c[0] if return_columns else ruler_area.c[1]
        rulers.append((curr_idx, ruler_pos))

        # Classify areas

        modeflags = (return_columns, use_ruler_pos, use_font_sizes)
        ruler_geometry = (ruler_pos, ruler_bounds)

        indexes = _algorithm(
            areas,
            indexes,
            ruler_geometry,
            curr_idx,
            modeflags,
            logic,
            font_sizes,
            font_tol_ratio=0.5,
        )

    # Sort rulers and create mapping
    mapping = {
        old: new for new, (old, _) in enumerate(sorted(rulers, key=lambda x: x[1]))
    }

    # Apply mapping
    return [mapping[idx] for idx in indexes]
