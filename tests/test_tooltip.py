"""Regression tests for TooltipTrigger class forwarding with custom render targets."""

import reflex as rx

from components.ui.tooltip import ClassNames, TooltipTrigger


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
