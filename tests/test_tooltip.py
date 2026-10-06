"""Regression tests for the Tooltip component wrapper around Base UI."""

import typing

import pytest
import reflex as rx

from components.ui.tooltip import (
    ClassNames,
    LiteralTrackCursorAxis,
    TooltipRoot,
    TooltipTrigger,
)


def test_tooltip_trigger_keeps_default_classes_without_render_target() -> None:
    trigger = TooltipTrigger.create()
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER in rendered_props


def test_tooltip_trigger_keeps_default_classes_with_native_render_targets() -> None:
    for target in (rx.el.div("target"), rx.el.a("target", href="#")):
        trigger = TooltipTrigger.create(render_=target)
        rendered_props = " ".join(trigger.render()["props"])

        assert ClassNames.TRIGGER in rendered_props
        assert "render:" in rendered_props


def test_tooltip_trigger_merges_custom_class_with_render_target() -> None:
    trigger = TooltipTrigger.create(
        render_=rx.el.div("target"), class_name="custom-trigger"
    )
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER in rendered_props
    assert "custom-trigger" in rendered_props


def test_tooltip_trigger_unstyled_omits_default_with_render_target() -> None:
    trigger = TooltipTrigger.create(
        render_=rx.el.div("target"), class_name="custom-trigger", unstyled=True
    )
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER not in rendered_props
    assert "custom-trigger" in rendered_props


def test_track_cursor_axis_accepts_both_and_rejects_bottom() -> None:
    """`track_cursor_axis` must match Base UI's `'none' | 'x' | 'y' | 'both'` contract."""
    accepted = set(typing.get_args(LiteralTrackCursorAxis))
    assert accepted == {"none", "x", "y", "both"}

    root = TooltipRoot.create(track_cursor_axis="both")
    assert 'trackCursorAxis:"both"' in " ".join(root.render()["props"])

    with pytest.raises(TypeError):
        TooltipRoot.create(track_cursor_axis="bottom")
