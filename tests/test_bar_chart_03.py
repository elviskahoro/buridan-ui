# noqa: INP001
"""Regression tests for the ``bar_chart_03`` "Average BPM" series toggle.

Introduced wholesale in commit 41be0dd ("new: blocks (#91)"), ``bar_chart_03``
toggled its Running/Cycling series by swapping a CSS opacity class on the
``rx.recharts.bar`` elements while the header "Average BPM" number was computed
through an exclusive ``rx.cond`` cascade over ``ShowRunning``/``ShowCycling``
(falling back to ``"0"`` when both off). The result was a self-contradictory
widget: with a series toggled off, 50%-opacity bars stayed on the chart, still
contributed to the hover tooltip and the y-axis scale, yet the headline number
reported the single-series average (or ``0 bpm`` with both off) — the summary
metric visibly disagreed with the rendered data.

The fix matches the codebase's only other toggleable-series block
(``bar_chart_01``): each ``rx.recharts.bar`` is wrapped in an ``rx.cond`` on its
``ClientStateVar`` so toggling removes the series entirely from the chart,
tooltip, and axis scale — keeping the header and chart in agreement. These
tests pin that exclusion semantics and guard against the dim-only regression
recurring.
"""

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.blocks.bar_chart_03 import bar_chart_03  # noqa: E402

# The block computes these from its static ``data`` table (running avg 143,
# cycling avg 125, overall avg 134); they appear ONLY in the header cascade, so
# their presence pins the header ``<p>``'s ``rx.cond`` cascade end-to-end.
_HEADER_OVERALL_AVG = "134"
_HEADER_RUNNING_AVG = "143"
_HEADER_CYCLING_AVG = "125"


def _iter_components(root: Any) -> Iterator[Any]:  # noqa: ANN401
    """Yield ``root`` and every descendant component, depth-first."""
    yield root
    for child in getattr(root, "children", ()):
        yield from _iter_components(child)


def _find_by_type_name(root: Any, type_name: str) -> list[Any]:  # noqa: ANN401
    return [c for c in _iter_components(root) if type(c).__name__ == type_name]


def _bar_charts(root: Any) -> list[Any]:  # noqa: ANN401
    charts = _find_by_type_name(root, "BarChart")
    assert charts, "bar_chart_03 must render at least one Recharts BarChart"
    return charts


def _cond_wrapped_bars(chart: Any) -> list[Any]:  # noqa: ANN401
    """Return the ``Cond`` nodes in ``chart`` whose true branch holds a ``Bar``.

    These are the series gated on a ``ClientStateVar``. The false branch must be
    an empty ``Fragment`` so the series is fully removed (not merely dimmed) when
    toggled off — that removal is what excludes it from the tooltip and axis.
    """
    wrapped = []
    for cond in _find_by_type_name(chart, "Cond"):
        branches = list(getattr(cond, "children", ()))
        if len(branches) == 2 and _find_by_type_name(branches[0], "Bar"):  # noqa: PLR2004
            wrapped.append(cond)
    return wrapped


def _bar_in(branch: Any) -> Any:  # noqa: ANN401
    bars = _find_by_type_name(branch, "Bar")
    assert len(bars) == 1, f"expected one Bar in cond branch, found {len(bars)}"
    return bars[0]


def _bar_props(bar: Any) -> str:  # noqa: ANN401
    return " ".join(bar.render()["props"])


def _cond_state(cond: Any) -> str:  # noqa: ANN401
    state = cond.render()["cond_state"]
    assert isinstance(state, str)
    return state


def _is_empty_fragment(component: Any) -> bool:  # noqa: ANN401
    return bool(
        type(component).__name__ == "Fragment"
        and not list(getattr(component, "children", ())),
    )


def test_each_chart_wraps_both_series_in_rx_cond() -> None:
    """Both toggled series must be ``rx.cond``-gated, matching ``bar_chart_01``.

    A dimming ``class_name`` ternary leaves the bar mounted (so it still feeds the
    tooltip and y-axis); wrapping the bar in ``rx.cond`` removes it. Each rendered
    BarChart (mobile + desktop) must gate exactly one Running cond and one Cycling
    cond, and each cond's false branch must be an empty Fragment.
    """
    for chart in _bar_charts(bar_chart_03()):
        conds = _cond_wrapped_bars(chart)
        assert len(conds) == 2, (  # noqa: PLR2004
            f"expected one cond-gated bar per series, found {len(conds)}"
        )

        false_branches = [list(getattr(c, "children", ()))[1] for c in conds]
        assert all(_is_empty_fragment(fb) for fb in false_branches), (
            "toggled-off series must be removed (empty Fragment), not dimmed"
        )


def test_running_cond_is_gated_on_show_running() -> None:
    """The Running bar cond must reference ``show_running`` and keep chart-2 fill."""
    for chart in _bar_charts(bar_chart_03()):
        running_conds = [
            c for c in _cond_wrapped_bars(chart) if "show_running" in _cond_state(c)
        ]
        assert len(running_conds) == 1, "expected exactly one cond on show_running"
        true_branch = next(iter(getattr(running_conds[0], "children", ())))
        props = _bar_props(_bar_in(true_branch))
        assert 'dataKey:"Running"' in props
        assert 'fill:"var(--chart-2)"' in props


def test_cycling_cond_is_gated_on_show_cycling() -> None:
    """The Cycling bar cond must reference ``show_cycling`` and keep chart-3 fill."""
    for chart in _bar_charts(bar_chart_03()):
        cycling_conds = [
            c for c in _cond_wrapped_bars(chart) if "show_cycling" in _cond_state(c)
        ]
        assert len(cycling_conds) == 1, "expected exactly one cond on show_cycling"
        true_branch = next(iter(getattr(cycling_conds[0], "children", ())))
        props = _bar_props(_bar_in(true_branch))
        assert 'dataKey:"Cycling"' in props
        assert 'fill:"var(--chart-3)"' in props


def test_header_average_cascade_preserved_and_reads_same_toggles() -> None:
    """The header ``<p>`` renders the average via an ``rx.cond`` cascade over the
    same ``show_running``/``show_cycling`` state the chart removes on: overall avg
    when both on, single-series avg when one on, ``0`` when both off. This is the
    correct half of the contract and must stay intact (and read the same vars the
    chart conds read) so the headline and chart can never disagree.
    """
    header_paragraphs = [
        c
        for c in _iter_components(bar_chart_03())
        if getattr(c, "tag", None) == "p" and _HEADER_RUNNING_AVG in str(c)
    ]
    assert len(header_paragraphs) == 1, "expected exactly one header average <p>"
    header = str(header_paragraphs[0])

    assert _HEADER_OVERALL_AVG in header, "both-on average (134) must remain"
    assert _HEADER_RUNNING_AVG in header, "running-only average (143) must remain"
    assert _HEADER_CYCLING_AVG in header, "cycling-only average (125) must remain"
    assert '"0"' in header, "both-off fallback (0) must remain"
    assert "show_running" in header, "header average must react to show_running"
    assert "show_cycling" in header, "header average must react to show_cycling"


def test_legend_click_toggles_the_same_vars_chart_and_header_read() -> None:
    """Closes the consistency loop: the clickable legend must write to
    ``show_running``/``show_cycling`` — the same ``ClientStateVar``s the chart
    conds (tests above) and the header cascade read — so a legend click moves the
    chart and the headline in lockstep.
    """
    on_click_js: list[str] = []
    for component in _iter_components(bar_chart_03()):
        triggers = getattr(component, "event_triggers", {}) or {}
        events = triggers.get("on_click")
        if not events:
            continue
        for event in events.events:
            on_click_js.append(getattr(event, "_js_expr", ""))
    joined = " ".join(on_click_js)
    assert "show_running" in joined, "legend on_click must toggle show_running"
    assert "show_cycling" in joined, "legend on_click must toggle show_cycling"
