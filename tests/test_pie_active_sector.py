"""Regression tests for the "Pie Chart - Active" demo (``piechart_v6``).

recharts 3 (pinned via ``reflex.lock/package.json`` -> ``recharts@3.10.1``)
removed ``activeIndex`` as a ``Pie`` prop: the active sector index now comes
exclusively from the chart's tooltip store (``selectActiveTooltipIndex``).
The demo previously set ``custom_attrs={"activeIndex": 1, ...}`` on
``rx.recharts.pie``, which recharts silently ignores, so the advertised
statically-highlighted sector never rendered.

The fix drives activeness through the supported state path -- a
``<Tooltip defaultIndex="1">`` pre-populates the tooltip state, and
``activeShape: {outerRadius: 110}`` styles the enlarged sector geometry.

These tests pin the recharts-3 mechanism and guard against a regression to
the inert recharts-2 ``activeIndex`` idiom (or the broken
``tooltip(default_index=...)`` kwarg form, which reflex routes into the
tooltip's ``wrapperStyle`` instead of a real prop).
"""

from __future__ import annotations

import pathlib
import sys

ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from reflex.components.component import Component

from app.www.library.charts.pie.v6 import piechart_v6

PIE_TAG = "Pie"
TOOLTIP_TAG = "Tooltip"


def _walk(component: Component):
    """Yield ``component`` and every descendant in render-tree order."""
    pending = [component]
    while pending:
        current = pending.pop()
        yield current
        pending.extend(
            child
            for child in getattr(current, "children", ())
            if isinstance(child, Component)
        )


def _find(component: Component, tag: str) -> Component:
    for node in _walk(component):
        if getattr(node, "tag", None) == tag:
            return node
    raise AssertionError(f"No <{tag}> component found in piechart_v6 render tree")


def test_pie_does_not_carry_inert_active_index_prop() -> None:
    """The recharts-2 ``activeIndex`` Pie prop is inert on recharts 3 and must
    not be re-introduced (it is silently ignored, masking the bug)."""
    rendered = str(piechart_v6())
    assert "activeIndex" not in rendered, (
        "piechart_v6 must not pass the inert recharts-2 `activeIndex` Pie prop; "
        "on recharts 3 the active index comes only from tooltip state."
    )


def test_pie_keeps_active_shape_enlarged_geometry() -> None:
    """``activeShape`` (still supported on recharts 3) supplies the enlarged
    sector geometry, so it must remain on the Pie with ``outerRadius: 110``."""
    pie = _find(piechart_v6(), PIE_TAG)
    assert "outerRadius" in str(pie.custom_attrs.get("activeShape", ""))
    rendered_pie = str(pie.render())
    assert "activeShape" in rendered_pie
    assert "outerRadius" in rendered_pie
    assert "110" in rendered_pie


def test_tooltip_is_rendered_inside_pie_chart() -> None:
    """A ``<Tooltip>`` must be rendered so the static active sector has a
    recharts-3-supported state path to draw from."""
    tooltip = _find(piechart_v6(), TOOLTIP_TAG)
    assert tooltip.tag == TOOLTIP_TAG


def test_tooltip_carries_default_index_prop_for_static_active_sector() -> None:
    """The static highlight is driven by ``<Tooltip defaultIndex=\"1\">``, the
    documented recharts-3 mechanism that pre-populates
    ``selectActiveTooltipIndex`` so sector #1 (safari) renders enlarged on
    first paint without any hover interaction."""
    tooltip = _find(piechart_v6(), TOOLTIP_TAG)
    assert tooltip.custom_attrs.get("defaultIndex") == "1"
    rendered = str(piechart_v6())
    assert 'defaultIndex:"1"' in rendered


def test_default_index_is_a_real_prop_not_leaked_into_wrapper_style() -> None:
    """Guard against the broken ``tooltip(default_index=\"1\")`` kwarg form.

    Passing ``default_index=`` as a direct kwarg (the naive reflex translation
    of ``<Tooltip defaultIndex>``) does NOT become a JSX prop -- reflex routes
    unknown kwargs into the component ``style`` dict, which recharts renders as
    ``wrapperStyle``. That leaves the active sector inert, reproducing the
    exact bug. The fix uses ``custom_attrs`` so ``defaultIndex`` reaches the
    ``<Tooltip>`` tag as a real prop.
    """
    tooltip = _find(piechart_v6(), TOOLTIP_TAG)
    # defaultIndex must be a custom_attr (real JSX prop), never a style key
    # (style keys are rendered by recharts as `wrapperStyle`, which the Tooltip
    # ignores for active-index purposes).
    assert "defaultIndex" not in {str(k) for k in (tooltip.style or {})}
    assert tooltip.custom_attrs.get("defaultIndex") == "1"
    assert 'defaultIndex:"1"' in str(tooltip.render())


def test_docs_snippet_does_not_advertise_inert_active_index_pattern() -> None:
    """The embedded docs snippet (the ``--DEMO(piechart_v6)--`` mirror in
    ``assets/docs/charts/pie-chart.md``) must not advertise the broken
    ``activeIndex`` prop -- users copy this snippet verbatim."""
    snippet_path = ROOT_DIR / "assets" / "docs" / "charts" / "pie-chart.md"
    assert snippet_path.is_file(), f"Missing generated snippet: {snippet_path}"
    snippet = snippet_path.read_text(encoding="utf-8")
    assert "activeIndex" not in snippet, (
        "assets/docs/charts/pie-chart.md still advertises the inert "
        "`activeIndex` Pie prop."
    )
    assert 'rx.recharts.tooltip(custom_attrs={"defaultIndex": "1"})' in snippet


def test_docs_snippet_is_in_sync_with_demo_source() -> None:
    """The generated pie-chart markdown must match what
    ``scripts/generate_markdown.py`` would regenerate from the demo source, so
    the CI ``git diff --exit-code assets/docs`` gate stays green and the docs
    never drift from the live demo."""
    from scripts.generate_markdown import (
        convert_to_pure_markdown,
        dynamic_load_components,
    )

    registry = dynamic_load_components(["app/www/library", "components/ui"])
    source_md = (ROOT_DIR / "docs" / "charts" / "pie_chart.md").read_text(
        encoding="utf-8",
    )
    expected = convert_to_pure_markdown(source_md, registry)
    on_disk = (ROOT_DIR / "assets" / "docs" / "charts" / "pie-chart.md").read_text(
        encoding="utf-8"
    )
    assert expected.strip() == on_disk.strip(), (
        "assets/docs/charts/pie-chart.md is out of sync with the demo source / "
        "docs/pie_chart.md -- run `uv run python scripts/generate_markdown.py`."
    )
