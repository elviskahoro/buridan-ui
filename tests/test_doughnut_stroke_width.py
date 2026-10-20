# ruff: noqa: INP001

"""Regression tests for the doughnut chart slice-separation stroke width.

The doughnut examples intend a 5px background-colored stroke between sectors.
``stroke_width`` is not a declared prop of ``reflex_components_recharts.Pie``,
so Reflex folds it into ``component.style``, which ``Recharts._get_style`` emits
as ``wrapperStyle`` (see ``reflex_components_recharts/recharts.py``). recharts'
``Pie`` ignores ``wrapperStyle`` entirely, so the stroke silently falls back to
the SVG default of ~1px. Passing ``strokeWidth`` through ``custom_attrs`` lands it
as a real top-level JSX prop on ``<Pie>``, which recharts honors on every sector.
"""

import reflex as rx
from reflex.components.component import Component

from app.www.library.charts.doughnut.v1 import doughnutchart_v1
from app.www.library.charts.doughnut.v2 import doughnutchart_v2

EXPECTED_STROKE_WIDTH = 5
EXPECTED_PADDING_ANGLE = 3
EXPECTED_CORNER_RADIUS = 5


def _find_pie(component: Component) -> Component:
    """Return the first ``Pie`` component in the tree, else AssertionError."""
    pending: list[Component] = [component]
    while pending:
        current = pending.pop()
        if getattr(current, "tag", None) == "Pie":
            return current
        pending.extend(
            child
            for child in getattr(current, "children", ())
            if isinstance(child, Component)
        )
    msg = "Doughnut chart demo does not contain a Pie component"
    raise AssertionError(msg)


def _rendered_props(pie: Component) -> str:
    return " ".join(str(prop) for prop in pie.render()["props"])


def test_doughnutchart_v1_pie_emits_top_level_stroke_width() -> None:
    """v1's ``Pie`` must render ``strokeWidth`` as a real prop, not ``wrapperStyle``."""
    pie = _find_pie(doughnutchart_v1())
    props = _rendered_props(pie)

    assert "strokeWidth:5" in props
    assert "wrapperStyle" not in props
    assert pie.style == {}
    assert pie.custom_attrs["strokeWidth"] == EXPECTED_STROKE_WIDTH
    assert pie.custom_attrs["paddingAngle"] == EXPECTED_PADDING_ANGLE
    assert pie.custom_attrs["cornerRadius"] == EXPECTED_CORNER_RADIUS
    assert 'stroke:"var(--background)"' in props
    assert "paddingAngle:3" in props
    assert "cornerRadius:5" in props
    assert "innerRadius:60" in props
    assert "isAnimationActive:false" in props


def test_doughnutchart_v2_pie_emits_top_level_stroke_width() -> None:
    """v2's ``Pie`` must render ``strokeWidth:5`` as a real prop, not ``wrapperStyle``."""
    pie = _find_pie(doughnutchart_v2())
    props = _rendered_props(pie)

    assert "strokeWidth:5" in props
    assert "wrapperStyle" not in props
    assert pie.style == {}
    assert pie.custom_attrs["strokeWidth"] == EXPECTED_STROKE_WIDTH
    assert 'stroke:"var(--background)"' in props
    assert "innerRadius:60" in props
    assert "isAnimationActive:false" in props


def test_pie_silently_routes_stroke_width_to_wrapper_style() -> None:
    """Pin why ``stroke_width`` must not be used as a kwarg on ``rx.recharts.pie``.

    Passing ``stroke_width`` (an undeclared prop) routes the value into
    ``component.style``, which ``Recharts`` serializes as ``wrapperStyle`` — a prop
    recharts' ``Pie`` ignores. This pins the bug mechanism so a future cleanup that
    moves ``strokeWidth`` back to a bare ``stroke_width`` kwarg fails loudly here.
    """
    pie = rx.recharts.pie(
        data=[{"browser": "chrome", "visitors": 275}],
        data_key="visitors",
        name_key="browser",
        inner_radius=60,
        stroke_width=EXPECTED_STROKE_WIDTH,
        stroke="var(--background)",
        is_animation_active=False,
    )
    props = _rendered_props(pie)

    assert "strokeWidth" in pie.style
    assert "wrapperStyle" in props
    assert "strokeWidth:5" not in props
