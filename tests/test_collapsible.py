"""Tests for the Collapsible panel's class_name shield.

``CollapsiblePanel`` carries the structural ``transition-[height]`` animation
on ``ClassNames.PANEL``. Because ``cn()`` resolves via tailwind-merge
(client-side), any user-supplied ``transition-*`` utility merged onto the *same*
element drops ``transition-[height]`` (same twMerge conflict group, last-wins).

``AccordionPanel`` was hardened in 755f3ed by popping the user's ``class_name``
off the panel props and routing it to an inner content wrapper, so the panel
element always retains its structural transition. These tests verify
``CollapsiblePanel`` adopts the same shield and that the escape hatches
(``unstyled``, ``render_``) keep working through the new code path.

``cn()`` returns a deferred reflex ``Var`` (a serialized JS call template), so
its ``str()`` form embeds both literal inputs — see ``tests/test_context_menu.py``
for the established assertion convention.
"""

import sys
from pathlib import Path
from typing import cast

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx
from reflex.components.component import Component

from components.ui.accordion import AccordionPanel
from components.ui.button import button
from components.ui.collapsible import (
    ClassNames,
    CollapsiblePanel,
    CollapsibleTrigger,
)
from components.ui.core import BaseUIComponent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _panel(class_name: str | None = None, **props) -> BaseUIComponent:
    """Build a panel with a single child, optionally passing class_name."""
    if class_name is None:
        return CollapsiblePanel.create(rx.el.div("content"), **props)
    return CollapsiblePanel.create(rx.el.div("content"), class_name=class_name, **props)


def _inner_div(panel: BaseUIComponent) -> Component:
    """Return the inner content wrapper (the panel's sole child).

    ``children`` is typed ``list[BaseComponent]`` and ``BaseComponent`` does not
    expose ``class_name``; the inner wrapper is an ``rx.el.div`` (a ``Component``),
    so we downcast to access the merged class_name Var.
    """
    children = panel.children
    assert len(children) == 1, "panel should wrap content in a single div"
    return cast(Component, children[0])


def _shielded_panel_class_name() -> str:
    """The exact serialized form the panel element must always take."""
    return f'(twMerge((clsx("{ClassNames.PANEL}", ""))))'


# ---------------------------------------------------------------------------
# Structural shield: the panel element never receives the user's class_name
# ---------------------------------------------------------------------------


def test_panel_wraps_children_in_a_single_inner_div() -> None:
    """The panel must wrap its children in a single inner ``rx.el.div``."""
    panel = _panel(class_name="custom-panel")
    inner = _inner_div(panel)
    assert type(inner).__name__ == "Div"
    assert getattr(inner, "tag", None) == "div"


def test_panel_default_inner_wrapper_is_empty() -> None:
    """Without a user class_name, the inner wrapper carries no styling (no double-padding)."""
    panel = _panel()
    assert str(_inner_div(panel).class_name) == '(twMerge((clsx("", ""))))'


def test_panel_class_name_is_always_shielded_from_user_class_name() -> None:
    """
    The panel element's class_name must be exactly ``cn(PANEL, "")`` regardless of
    what the caller passes — the user's class_name is never merged onto the
    transition-bearing panel element. This is the structural guarantee that
    shields ``transition-[height]`` from tailwind-merge conflicts.
    """
    panel = _panel(class_name="transition-[opacity] duration-500")
    assert str(panel.class_name) == _shielded_panel_class_name()


# ---------------------------------------------------------------------------
# The bug: user-supplied transition-* must not drop transition-[height]
# ---------------------------------------------------------------------------


def test_panel_keeps_height_transition_for_transition_star_utilities() -> None:
    """
    Regression for the height-animation bug: any ``transition-*`` utility passed
    via ``class_name`` shares tailwind-merge's transition-property conflict group
    with the structural ``transition-[height]`` and would drop it if merged onto
    the panel element. The panel must keep ``transition-[height]`` and route the
    user utility to the inner wrapper.
    """
    for user_class in (
        "transition-all",
        "transition-opacity",
        "transition-colors",
        "transition-transform",
        "transition",
        "transition-[background-color]",
        "transition-[opacity] duration-500",
    ):
        panel = _panel(class_name=user_class)
        # Panel element is always exactly cn(PANEL, "") — transition-[height] survives.
        assert str(panel.class_name) == _shielded_panel_class_name(), (
            f"panel element changed for user class {user_class!r}"
        )
        assert "transition-[height]" in str(panel.class_name)
        # The user utility routes to the inner wrapper, not the panel element.
        assert user_class in str(_inner_div(panel).class_name), (
            f"user class {user_class!r} not routed to inner wrapper"
        )


def test_panel_routes_non_conflicting_user_classes_to_inner_wrapper_too() -> None:
    """
    The shield is unconditional: non-conflicting utilities also route to the inner
    wrapper (the panel element is *always* ``cn(PANEL, "")``), bringing Collapsible
    into architectural parity with Accordion — callers cannot style the animated
    panel box directly via ``class_name``.
    """
    for user_class in ("duration-500", "bg-blue-500 p-4", "border-t border-border/40"):
        panel = _panel(class_name=user_class)
        assert str(panel.class_name) == _shielded_panel_class_name()
        assert user_class in str(_inner_div(panel).class_name)


# ---------------------------------------------------------------------------
# Escape hatches still work through the new code path
# ---------------------------------------------------------------------------


def test_panel_unstyled_omits_default_classes() -> None:
    """unstyled=True bypasses the default PANEL class on the panel element."""
    panel = _panel(class_name="custom", unstyled=True)
    assert str(panel.class_name) == ""


def test_panel_render_skips_default_class_merge() -> None:
    """
    render_ is a full-replacement escape hatch: the panel element receives no
    default class, while the user's class_name still routes to the inner wrapper.
    """
    panel = CollapsiblePanel.create(
        rx.el.div("content"),
        class_name="transition-[opacity]",
        render_=rx.el.div("replacement"),
    )
    assert panel.class_name is None
    assert "transition-[opacity]" in str(_inner_div(panel).class_name)


def test_trigger_render_preserves_target_classes_without_component_defaults() -> None:
    trigger = CollapsibleTrigger.create(
        render_=button("toggle"), class_name="custom-trigger"
    )
    rendered_props = " ".join(trigger.render()["props"])

    assert ClassNames.TRIGGER not in rendered_props
    assert "custom-trigger" in rendered_props
    assert "render:" in rendered_props


# ---------------------------------------------------------------------------
# Parity with AccordionPanel (the established shield pattern)
# ---------------------------------------------------------------------------


def test_panel_shield_matches_accordion_panel_shield() -> None:
    """
    CollapsiblePanel and AccordionPanel must shield the panel element's
    ``transition-[height]`` the same way: the panel element's class_name is
    ``cn(<default PANEL>, "")`` and the user class_name lands on an inner div.
    This guards against the two components diverging again — the divergence
    between them is exactly what introduced this bug.
    """
    cpanel = CollapsiblePanel.create(
        rx.el.div("c"), class_name="transition-[opacity] duration-500"
    )
    apanel = AccordionPanel.create(
        rx.el.div("a"), class_name="transition-[opacity] duration-500"
    )

    assert "transition-[height]" in str(cpanel.class_name)
    assert "transition-[height]" in str(apanel.class_name)
    assert "transition-[opacity]" not in str(cpanel.class_name)
    assert "transition-[opacity]" not in str(apanel.class_name)
    assert "transition-[opacity]" in str(_inner_div(cpanel).class_name)
    assert "transition-[opacity]" in str(_inner_div(apanel).class_name)
