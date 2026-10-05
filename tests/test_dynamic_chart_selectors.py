"""Regression tests for the interactive chart demo selectors."""

from app.www.library.charts.area.v5 import areachart_v5
from app.www.library.charts.bar.v5 import barchart_v5
from app.www.library.charts.line.v7 import linechart_v7


def _find_select(component):
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
    raise AssertionError("Chart demo does not contain a select element")


def _assert_select_wiring(factory, expected_default, expected_values):
    select = _find_select(factory())

    assert select.default_value._var_value == expected_default
    assert [option.value._var_value for option in select.children] == expected_values
    assert "on_change" in select.event_triggers
    on_change_js = select.event_triggers["on_change"].events[0]._js_expr
    assert "_client_state_set" in on_change_js
    assert "target" in on_change_js and "value" in on_change_js
    assert all("on_click" not in option.event_triggers for option in select.children)


def test_area_chart_range_selector_uses_parent_change_event():
    _assert_select_wiring(
        areachart_v5,
        "last_3_months",
        ["last_3_months", "last_30_days", "last_7_days"],
    )


def test_bar_chart_device_selector_uses_parent_change_event():
    _assert_select_wiring(barchart_v5, "mobile", ["mobile", "desktop"])


def test_line_chart_device_selector_uses_parent_change_event():
    _assert_select_wiring(linechart_v7, "mobile", ["mobile", "desktop"])
