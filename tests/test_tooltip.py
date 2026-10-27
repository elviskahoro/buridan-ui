"""Regression tests for the Tooltip component wrapper around Base UI."""

import typing

import pytest
import reflex as rx

from components.ui.tooltip import (
    ClassNames,
    LiteralTrackCursorAxis,
    TooltipPopup,
    TooltipProvider,
    TooltipRoot,
    TooltipTrigger,
)


class _UnstyledState(rx.State):  # pyright: ignore[reportUntypedBaseClass]
    """State exposing a boolean Var for the dynamic ``unstyled`` escape hatch."""

    flag: bool = False


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
        render_=rx.el.div("target"),
        class_name="custom-trigger",
    )
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER in rendered_props
    assert "custom-trigger" in rendered_props


def test_tooltip_trigger_unstyled_omits_default_with_render_target() -> None:
    trigger = TooltipTrigger.create(
        render_=rx.el.div("target"),
        class_name="custom-trigger",
        unstyled=True,
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


def test_tooltip_trigger_render_with_var_unstyled_does_not_crash() -> None:
    """A ``Var[bool]`` passed as ``unstyled`` alongside ``render_`` must not crash
    component construction. Regression for the ``_merge_default_classes_with_render``
    flag in #66, which removed the ``render_`` early-return shield and exposed a
    Python ``bool(<Var>)`` truthiness check that raises ``VarTypeError``.
    """
    trigger = TooltipTrigger.create(
        render_=rx.el.div("target"),
        unstyled=_UnstyledState.flag,
    )
    rendered_props = " ".join(trigger.render()["props"])

    assert "render:" in rendered_props
    assert ClassNames.TRIGGER in rendered_props


def test_tooltip_trigger_var_unstyled_without_render_does_not_crash() -> None:
    """The non-``render_`` path shared the same ``if <Var>:`` truthiness defect and
    crashed identically before the fix. Both routes must tolerate a ``Var[bool]``.
    """
    trigger = TooltipTrigger.create(unstyled=_UnstyledState.flag)
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER in rendered_props


def test_tooltip_trigger_var_unstyled_toggles_classes_dynamically() -> None:
    """The dynamic escape hatch must be honored at render time rather than silently
    discarded: the emitted ``class_name`` is a ``cond`` selecting the caller's class
    when the Var is true and the merged defaults otherwise.
    """
    trigger = TooltipTrigger.create(
        render_=rx.el.div("target"),
        class_name="custom",
        unstyled=_UnstyledState.flag,
    )
    class_name = str(trigger.class_name)

    # The class name is gated on the Var via a ternary (rx.cond), not stripped.
    assert "?" in class_name
    # The caller's class survives in both branches of the toggle.
    assert "custom" in class_name
    # The default classes appear in the merged (false) branch.
    assert ClassNames.TRIGGER in class_name


def test_tooltip_trigger_var_unstyled_with_custom_class_preserves_caller_class() -> (
    None
):
    """The caller's ``class_name`` is the unstyled value and is merged into the
    defaults branch, so it must appear in the emitted toggle on both sides.
    """
    trigger = TooltipTrigger.create(
        class_name="custom-trigger",
        unstyled=_UnstyledState.flag,
    )
    class_name = str(trigger.class_name)

    assert "custom-trigger" in class_name
    assert ClassNames.TRIGGER in class_name


def test_tooltip_popup_render_with_var_unstyled_does_not_crash() -> None:
    """``TooltipPopup`` keeps the ``render_`` early-return shield, so a ``Var[bool]``
    passed as ``unstyled`` must still be tolerated (parity with the pre-#66 path).
    """
    popup = TooltipPopup.create(
        render_=rx.el.div("popup"),
        unstyled=_UnstyledState.flag,
    )
    rendered_props = " ".join(popup.render()["props"])

    assert "render:" in rendered_props
    assert ClassNames.POPUP not in rendered_props


# ---------------------------------------------------------------------------
# Base UI 1.6.0 dead-prop audit (parity with DialogRoot.dismissible)
# ---------------------------------------------------------------------------


def test_tooltip_root_no_longer_declares_dead_delay_props() -> None:
    """``delay``/``close_delay`` are not 1.6.0 ``Tooltip.Root`` props -- they live
    on ``Tooltip.Provider``/``Tooltip.Trigger``. Declaring them on Root was a
    silent no-op (same dead-prop pattern as ``DialogRoot.dismissible``). The
    audit removes them; the capability is preserved via ``TooltipProvider``
    (see ``test_tooltip_provider_still_exposes_delay_props``).
    """
    props = TooltipRoot.get_props()
    assert "delay" not in props
    assert "close_delay" not in props


def test_tooltip_root_hoverable_renamed_to_disable_hoverable_popup() -> None:
    """1.6.0 renamed ``hoverable`` -> ``disableHoverablePopup`` (inverted:
    ``hoverable={false}`` == ``disableHoverablePopup={true}``; defaults align at
    "hoverable" behavior). The wrapper exposes the 1.6.0 name and no longer
    offers the dead ``hoverable`` prop.
    """
    props = TooltipRoot.get_props()
    assert "hoverable" not in props
    assert "disable_hoverable_popup" in props

    rendered = " ".join(
        TooltipRoot.create(disable_hoverable_popup=True).render()["props"]
    )
    assert "disableHoverablePopup:true" in rendered
    assert "css:" not in rendered


def test_tooltip_provider_still_exposes_delay_props() -> None:
    """Removing ``delay``/``close_delay`` from Root must not lose the capability:
    ``TooltipProvider`` declares them (matching 1.6.0's ``TooltipProviderProps``),
    which is the correct component and how the app already uses them
    (``tooltip.provider(delay=0)``). Hover-delay config remains available.
    """
    props = TooltipProvider.get_props()
    assert "delay" in props
    assert "close_delay" in props
    assert "timeout" in props

    assert "delay:0" in " ".join(TooltipProvider.create(delay=0).render()["props"])
    assert "closeDelay:300" in " ".join(
        TooltipProvider.create(close_delay=300).render()["props"],
    )
