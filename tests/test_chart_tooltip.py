# noqa: INP001
"""Regression tests for the chart tooltip swatch-to-series mapping.

``chart_tooltip_content`` styles each recharts tooltip row with a color swatch
via ``nth-child(i)`` CSS selectors. Recharts (pinned by Reflex at 3.10.1) sorts
tooltip items by ``itemSorter: 'name'`` before rendering, so the i-th rendered
``.recharts-tooltip-item`` is the i-th series name in *ascending* order — not
the series-declaration order. The pre-fix helper emitted ``nth-child(i)``
selectors assuming DOM order == ``chart_colors`` declaration order, so any
chart whose series names are not alphabetically ordered the same way as their
color declaration rendered swatches on the wrong rows — e.g. the ``Inverters``
row carried the ``SolarPanels`` (``--chart-1``) swatch.

The fix adds an optional ``series_names`` argument: when provided, the helper
pairs each name with the ``chart_colors`` entry at the same position
(``series_names[i]`` is the ``data_key`` whose stroke/fill is
``var(--chart-{chart_colors[i]})``), sorts the pairs by name (the order
Recharts renders), and emits the ``nth-child(i)`` swatch for the color that
lands at position i. When omitted, the helper keeps the legacy
declaration-order behavior (correct only when names are already alphabetical).
The twin copy at ``app/www/library/charts/chart_tooltip.py`` must stay in
lockstep with ``components/charts/chart_tooltip.py``.

These tests verify: the helper's name-sorted mapping, the backward-compatible
fallback when ``series_names`` is omitted, the three swatch shapes, the
length-mismatch guard, the twin-copy invariant, and the end-to-end wiring of
the shipped charts — the tooltip ``class_name`` emitted by each affected
chart's card must map each ``nth-child`` swatch to the color of the series
Recharts renders in that row.
"""

import re
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from reflex.components.component import Component

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.blocks.area_chart_01 import area_chart_01  # noqa: E402
from app.www.library.blocks.area_chart_02 import area_chart_02  # noqa: E402
from app.www.library.blocks.bar_chart_01 import bar_chart_01  # noqa: E402
from app.www.library.blocks.bar_chart_02 import bar_chart_02  # noqa: E402
from app.www.library.blocks.bar_chart_03 import bar_chart_03  # noqa: E402
from app.www.library.blocks.line_chart_02 import line_chart_02  # noqa: E402
from app.www.library.blocks.line_chart_03 import line_chart_03  # noqa: E402
from app.www.library.blocks.line_chart_04 import line_chart_04  # noqa: E402
from app.www.library.charts.area.v4 import areachart_v4  # noqa: E402
from app.www.library.charts.area.v6 import areachart_v6  # noqa: E402
from app.www.library.charts.area.v7 import areachart_v7  # noqa: E402
from app.www.library.charts.area.v10 import areachart_v10  # noqa: E402
from app.www.library.charts.bar.v9 import barchart_v9  # noqa: E402
from app.www.library.charts.chart_tooltip import (  # noqa: E402
    chart_tooltip_content as _app_helper,
)
from components.charts.chart_tooltip import Swatch, chart_tooltip_content  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SWATCH_RE = re.compile(
    r"recharts-tooltip-item:nth-child\((\d+)\)\]:before:!bg-\[var\(--chart-(\d+)\)\]",
)


def _swatch_map(classes: str) -> dict[int, int]:
    """Parse the ``nth-child`` position -> ``--chart-N`` mapping emitted by
    ``chart_tooltip_content`` from a string of Tailwind classes.

    Returns an empty dict for the ``border`` swatch (which styles the label,
    not the per-item rows and therefore emits no ``nth-child`` swatches).
    """
    return {int(pos): int(color) for pos, color in _SWATCH_RE.findall(classes)}


def _card_class_name(component: Component) -> str:
    """Serialize a chart card's merged ``class_name`` Var to a string, the
    established assertion convention for ``cn()``-merged classes (see
    ``tests/test_collapsible.py``): the literal caller classes are embedded
    inside the serialized ``twMerge(clsx(...))`` call.
    """
    return str(component.class_name)


# ---------------------------------------------------------------------------
# Legacy fallback: series_names omitted -> declaration order (no regression)
# ---------------------------------------------------------------------------


def test_legacy_path_without_series_names_assigns_colors_in_declaration_order() -> None:
    """Omitting ``series_names`` keeps the historical declaration-order mapping
    so every existing single-series chart and every chart whose names happen to
    be alphabetical continues to render identically — the fix is opt-in.
    """
    assert _swatch_map(chart_tooltip_content([1, 2], "square")) == {1: 1, 2: 2}
    assert _swatch_map(chart_tooltip_content([1, 2, 3], "line")) == {1: 1, 2: 2, 3: 3}
    assert _swatch_map(chart_tooltip_content([2, 3], "square")) == {1: 2, 2: 3}


def test_legacy_and_named_match_when_names_already_alphabetical() -> None:
    """For a chart whose declaration order already matches name-ascending order,
    passing ``series_names`` must produce the SAME mapping as the legacy path —
    no behavioral drift for the demos that were rendering correctly.
    """
    for colors, names in (
        ([1, 2], ["desktop", "mobile"]),
        ([1, 2, 3], ["desktop", "mobile", "tablet"]),
        ([1, 2], ["Organic", "Sponsored"]),
    ):
        assert chart_tooltip_content(colors, "square") == chart_tooltip_content(
            colors,
            "square",
            series_names=names,
        )


# ---------------------------------------------------------------------------
# The fix: series_names sorts the swatch mapping into Recharts' name order
# ---------------------------------------------------------------------------


def test_series_names_sorts_two_series_into_ascending_name_order() -> None:
    """line_chart_04 declares SolarPanels (--chart-1) then Inverters (--chart-2),
    but Recharts renders Inverters first (itemSorter: 'name'). The swatch on the
    first row must therefore be --chart-2 (Inverters), and --chart-1 (SolarPanels)
    on the second — the exact inverse of the pre-fix positional mapping.
    """
    out = chart_tooltip_content(
        [1, 2],
        "line",
        series_names=["SolarPanels", "Inverters"],
    )
    assert _swatch_map(out) == {1: 2, 2: 1}


def test_series_names_sorts_three_series_into_ascending_name_order() -> None:
    """line_chart_02 declares Munich (-1), Zurich (-2), Vienna (-3); Recharts
    renders Munich, Vienna, Zurich. So Vienna must take the --chart-3 swatch at
    position 2 and Zurich the --chart-2 swatch at position 3.
    """
    out = chart_tooltip_content(
        [1, 2, 3],
        "line",
        series_names=["Munich", "Zurich", "Vienna"],
    )
    assert _swatch_map(out) == {1: 1, 2: 3, 3: 2}


def test_series_names_pairs_color_with_the_series_that_owns_it() -> None:
    """``series_names[i]`` is the ``data_key`` whose stroke/fill is
    ``var(--chart-{chart_colors[i]})`` — not the i-th declared bar/line/area.
    bar_chart_02 declares 'Last Year' (--chart-2) BEFORE 'This Year' (--chart-1)
    but passes ``chart_colors=[1, 2]``, so here chart-1 is 'This Year' and
    chart-2 is 'Last Year'. Sorted by name, 'Last Year' renders first and must
    carry --chart-2; 'This Year' second with --chart-1.
    """
    out = chart_tooltip_content(
        [1, 2],
        "square",
        series_names=["This Year", "Last Year"],
    )
    assert _swatch_map(out) == {1: 2, 2: 1}

    # area/v6 declares mobile (--chart-1) before desktop (--chart-2): after
    # name-sorting, 'desktop' lands first and must take --chart-2.
    out = chart_tooltip_content([1, 2], "square", series_names=["mobile", "desktop"])
    assert _swatch_map(out) == {1: 2, 2: 1}


def test_series_names_handles_non_zero_offset_colors() -> None:
    """bar_chart_03 uses --chart-2 (Running) and --chart-3 (Cycling) — the color
    list does not start at 1. After sorting, 'Cycling' renders first and must
    take --chart-3; 'Running' second with --chart-2.
    """
    out = chart_tooltip_content([2, 3], "square", series_names=["Running", "Cycling"])
    assert _swatch_map(out) == {1: 3, 2: 2}


def test_single_series_is_a_noop_sort() -> None:
    """A single-series chart has only one tooltip row regardless of name, so
    passing ``series_names`` must not change the single swatch position/color.
    """
    assert _swatch_map(chart_tooltip_content([7], "square", series_names=["x"])) == {
        1: 7,
    }
    assert chart_tooltip_content([7], "square") == chart_tooltip_content(
        [7],
        "square",
        series_names=["x"],
    )


# ---------------------------------------------------------------------------
# Swatch shapes
# ---------------------------------------------------------------------------


def test_line_swatch_emits_pill_shape_utilities() -> None:
    out = chart_tooltip_content([1, 2], "line", series_names=["b", "a"])
    assert ":before:!h-0.5" in out
    assert ":before:!rounded-full" in out
    assert ":before:!h-3" not in out


def test_square_swatch_emits_box_shape_utilities() -> None:
    out = chart_tooltip_content([1, 2], "square", series_names=["b", "a"])
    assert ":before:!h-3" in out
    assert ":before:!rounded-sm" in out
    assert ":before:!h-0.5" not in out


def test_border_swatch_uses_first_color_and_emits_no_nth_child_swatch() -> None:
    """The ``border`` swatch styles the tooltip *label* (a single left accent
    line using ``chart_colors[0]``), not the per-item rows, so it must emit no
    ``nth-child`` swatches and must ignore ``series_names`` entirely.
    """
    out = chart_tooltip_content([5], "border", series_names=["anything"])
    assert "var(--chart-5)" in out
    assert "recharts-tooltip-label" in out
    assert _swatch_map(out) == {}
    assert chart_tooltip_content([5], "border") == out


def test_base_classes_are_present_on_every_non_border_swatch() -> None:
    out = chart_tooltip_content([1, 2], "square", series_names=["mobile", "desktop"])
    for base in (
        "[&_.recharts-tooltip-item-name]:!text-muted-foreground",
        "[&_.recharts-tooltip-item]:!flex",
        "[&_.recharts-tooltip-item]:!gap-2",
    ):
        assert base in out


# ---------------------------------------------------------------------------
# Validation guard
# ---------------------------------------------------------------------------


def test_length_mismatch_between_chart_colors_and_series_names_raises() -> None:
    with pytest.raises(
        ValueError,
        match="series_names must match chart_colors",
    ) as excinfo:
        chart_tooltip_content([1, 2], "square", series_names=["only one"])
    message = str(excinfo.value)
    assert "series_names" in message
    assert "chart_colors" in message
    assert "1" in message
    assert "2" in message


def test_series_names_empty_lists_match() -> None:
    """A zero-series edge case must not raise on the length guard (both empty)."""
    out = chart_tooltip_content([], "square", series_names=[])
    assert _swatch_map(out) == {}


# ---------------------------------------------------------------------------
# Twin-copy invariant: components/charts == app/www/library/charts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("colors", "swatch", "names"),
    [
        ([1, 2], "line", ["SolarPanels", "Inverters"]),
        ([1, 2, 3], "line", ["Munich", "Zurich", "Vienna"]),
        ([2, 3], "square", ["Running", "Cycling"]),
        ([1, 2], "square", ["mobile", "desktop"]),
        ([1, 2], "square", None),
        ([1], "border", None),
        ([5], "border", ["x"]),
        ([1, 2, 3], "square", ["desktop", "mobile", "tablet"]),
    ],
)
def test_twin_copies_produce_identical_output(
    colors: list[int],
    swatch: Swatch,
    names: list[str] | None,
) -> None:
    assert chart_tooltip_content(colors, swatch, series_names=names) == _app_helper(
        colors,
        swatch,
        series_names=names,
    )


# ---------------------------------------------------------------------------
# End-to-end: the shipped charts emit the corrected class_name on their card
# ---------------------------------------------------------------------------

_AFFECTED = [
    pytest.param(line_chart_04, {1: 2, 2: 1}, id="line_chart_04"),
    pytest.param(line_chart_02, {1: 1, 2: 3, 3: 2}, id="line_chart_02"),
    pytest.param(line_chart_03, {1: 2, 2: 1}, id="line_chart_03"),
    pytest.param(bar_chart_01, {1: 2, 2: 1}, id="bar_chart_01"),
    pytest.param(bar_chart_02, {1: 2, 2: 1}, id="bar_chart_02"),
    pytest.param(bar_chart_03, {1: 3, 2: 2}, id="bar_chart_03"),
    pytest.param(areachart_v6, {1: 2, 2: 1}, id="area_v6"),
    pytest.param(areachart_v7, {1: 2, 2: 1}, id="area_v7"),
    pytest.param(areachart_v10, {1: 2, 2: 1}, id="area_v10"),
    pytest.param(area_chart_02, {1: 1, 2: 2}, id="area_chart_02"),
]

_NO_REGRESSION = [
    pytest.param(area_chart_01, {1: 1, 2: 2}, id="area_chart_01"),
    pytest.param(areachart_v4, {1: 1, 2: 2}, id="area_v4"),
    pytest.param(barchart_v9, {1: 1, 2: 2, 3: 3}, id="bar_v9"),
]


@pytest.mark.parametrize(("factory", "expected"), _AFFECTED + _NO_REGRESSION)
def test_shipped_chart_tooltip_swatches_match_rendered_series(
    factory: Callable[[], Component],
    expected: dict[int, int],
) -> None:
    """Each shipped chart's card ``class_name`` must map every ``nth-child``
    swatch to the ``--chart-N`` of the series Recharts renders in that row.

    For the previously-bug-affected charts (line_chart_04, line_chart_02, etc.)
    this asserts the bug is fixed; for the alphabetically-ordered charts it
    asserts no regression — their mapping is unchanged by the sort.
    """
    assert _swatch_map(_card_class_name(factory())) == expected
