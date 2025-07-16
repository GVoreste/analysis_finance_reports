"""Utilities for selecting or deselecting lines or getting infos based of geometrical information"""

from typing import List
from enum import Flag, Enum, auto

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


class TablePosAlgorithm(Flag):
    ROW = auto()
    BIG_RULE = auto()
    RULER_AREA = auto()
    TEST_POS = auto()


class TablePosMeasureUnit(Enum):
    EM = auto()
    PERC = auto()
    PT = auto()


def _area_position_algorithm(
    ruler_geometry, test_geometry, algorithm_flags, abs_tolerance
):
    test_pos, test_bounds = test_geometry
    ruler_pos, ruler_bounds = ruler_geometry
    if TablePosAlgorithm.RULER_AREA in algorithm_flags:
        match_pos = test_pos
        min_bound, max_bound = ruler_bounds
    else:
        match_pos = ruler_pos
        min_bound, max_bound = test_bounds

    return (min_bound - abs_tolerance) <= match_pos <= (max_bound + abs_tolerance)


def _area_intersection_algorithm(
    ruler_geometry, test_geometry, algorithm_flags, abs_tolerance
):
    test_bounds = test_geometry[1]
    ruler_bounds = ruler_geometry[1]
    min_bound_t, max_bound_t = test_bounds
    min_bound_r, max_bound_r = ruler_bounds

    return (
        (min_bound_r - abs_tolerance) <= max_bound_t <= (max_bound_r + abs_tolerance)
    ) or ((min_bound_r - abs_tolerance) <= min_bound_t <= (max_bound_r + abs_tolerance))


def _algorithm_table_pos(ruler_geometry, test_geometry, algorithm_flags, abs_tolerance):
    if (TablePosAlgorithm.RULER_AREA in algorithm_flags) and (
        TablePosAlgorithm.TEST_POS not in algorithm_flags
    ):
        return _area_intersection_algorithm(
            ruler_geometry, test_geometry, algorithm_flags, abs_tolerance
        )
    else:
        return _area_position_algorithm(
            ruler_geometry, test_geometry, algorithm_flags, abs_tolerance
        )


def get_table_positions(
    lines: List[ExtractedPdfLine],
    algorithm_flags: TablePosAlgorithm = TablePosAlgorithm(0),
    tolerance: float = 0,
    tolerance_mu: TablePosMeasureUnit = TablePosMeasureUnit.EM,
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
    choose = max if TablePosAlgorithm.BIG_RULE in algorithm_flags else min
    return_col = TablePosAlgorithm.ROW not in algorithm_flags
    while None in indexes:
        curr_idx = len(rulers)
        # Get unindexed areas
        unindexed = [
            (i, area.width if return_col else area.height)
            for i, area in enumerate(areas)
            if indexes[i] is None
        ]

        # Select ruler for this axis
        ruler_idx, _ = choose(unindexed, key=lambda x: x[1])
        ruler_area = areas[ruler_idx]

        # Get ruler bounds and position
        ruler_bounds = ruler_area.x_bounds if return_col else ruler_area.y_bounds
        ruler_pos = ruler_area.c[0] if return_col else ruler_area.c[1]
        rulers.append((curr_idx, ruler_pos))

        # Classify areas

        ruler_geometry = (ruler_pos, ruler_bounds)
        for i, table_pos in enumerate(indexes):
            if table_pos is not None:
                continue
            test_bounds = areas[i].x_bounds if return_col else areas[i].y_bounds
            test_pos = areas[i].c[0] if return_col else areas[i].c[1]
            test_geometry = (test_pos, test_bounds)
            effective_tolerance = 0
            if tolerance_mu == TablePosMeasureUnit.PT:
                effective_tolerance = tolerance
            elif tolerance_mu == TablePosMeasureUnit.PERC:
                effective_tolerance = (
                    tolerance * areas[i].width if return_col else areas[i].height
                )
            elif tolerance_mu == TablePosMeasureUnit.EM:
                effective_tolerance = tolerance * font_sizes[i]

            if _algorithm_table_pos(
                ruler_geometry=ruler_geometry,
                test_geometry=test_geometry,
                algorithm_flags=algorithm_flags,
                abs_tolerance=effective_tolerance,
            ):
                indexes[i] = curr_idx

    # Sort rulers and create mapping
    mapping = {
        old: new for new, (old, _) in enumerate(sorted(rulers, key=lambda x: x[1]))
    }

    # Apply mapping
    return [mapping[idx] for idx in indexes]
