"""Regression tests for the interactive chart demo selectors."""

from collections.abc import Callable

import reflex as rx

from app.www.library.charts.area.v5 import areachart_v5
from app.www.library.charts.bar.v5 import barchart_v5
from app.www.library.charts.line.v7 import linechart_v7
from tests.render_helpers import event_triggers


def _find_select(component: rx.Component) -> rx.Component:
    pending = [component]
    while pending:
        current = pending.pop()
        if getattr(current, "tag", None) == "select":
            return current
        pending.extend(
            child
            for child in getattr(current, "children", ())
            if hasattr(child, "children")
        )
    msg = "Chart demo does not contain a select element"
    raise AssertionError(msg)


def _assert_select_wiring(
    factory: Callable[[], rx.Component],
    expected_default: str,
    expected_values: list[str],
) -> None:
    select = _find_select(factory())

    assert getattr(select, "default_value")._var_value == expected_default  # noqa: B009, SLF001
    assert [
        getattr(option, "value")._var_value  # noqa: B009, SLF001
        for option in select.children
    ] == expected_values
    assert "on_change" in event_triggers(select)
    on_change_js = event_triggers(select)["on_change"].events[0]._js_expr  # noqa: SLF001
    assert "_client_state_set" in on_change_js
    assert "target" in on_change_js
    assert "value" in on_change_js
    assert all(
        "on_click" not in getattr(option, "event_triggers")  # noqa: B009
        for option in select.children
    )


def test_area_chart_range_selector_uses_parent_change_event() -> None:
    _assert_select_wiring(
        areachart_v5,
        "last_3_months",
        ["last_3_months", "last_30_days", "last_7_days"],
    )


def test_bar_chart_device_selector_uses_parent_change_event() -> None:
    _assert_select_wiring(barchart_v5, "mobile", ["mobile", "desktop"])


def test_line_chart_device_selector_uses_parent_change_event() -> None:
    _assert_select_wiring(linechart_v7, "mobile", ["mobile", "desktop"])
