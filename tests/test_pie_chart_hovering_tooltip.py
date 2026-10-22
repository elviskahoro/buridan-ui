# noqa: INP001
"""Regression test for the pie-chart "Hovering Labels" demo (piechart_v2).

The docs page (`docs/charts/pie_chart.md`) advertises a "Hovering Labels" section that
"Displays labels that appear dynamically when hovering over chart segments." That hover
feedback is provided by a ``graphing_tooltip`` child of ``rx.recharts.pie_chart``.
The tooltip was silently dropped during the v0.9.0 file move (commit 7d27209) while the
docs description was left unchanged, so this test guards against the tooltip being
removed again and the documented behavior regressing.
"""

import reflex as rx

from app.www.library.charts.pie.v2 import piechart_v2


def _find_by_tag(component: rx.Component, tag: str) -> rx.Component:
    pending = [component]
    while pending:
        current = pending.pop()
        if getattr(current, "tag", None) == tag:
            return current
        pending.extend(
            child
            for child in getattr(current, "children", ())
            if hasattr(child, "children")
        )
    msg = f"Component tree does not contain a {tag!r} node"
    raise AssertionError(msg)


def test_piechart_v2_renders_a_hover_tooltip() -> None:
    """The "Hovering Labels" demo must include a graphing_tooltip child of the pie chart
    so that hovering a segment produces feedback, matching the documented behavior and
    the repo's other chart demos (bar/v5, area/v1, ...).
    """
    pie_chart = _find_by_tag(piechart_v2(), "PieChart")

    tooltip_nodes = [
        node
        for node in [pie_chart, *getattr(pie_chart, "children", ())]
        if getattr(node, "tag", None) == "Tooltip"
    ]

    assert len(tooltip_nodes) == 1, (
        "The 'Hovering Labels' pie demo must include a single graphing_tooltip child of "
        "rx.recharts.pie_chart so hovering a segment shows feedback."
    )
    assert type(tooltip_nodes[0]).__name__ == "GraphingTooltip"
