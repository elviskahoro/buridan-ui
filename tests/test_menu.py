"""Regression tests for the Menu wrapper.

Covers two audits of ``components/ui/menu.py``:

1. Dead Base UI 1.6.0 props. ``MenuRoot`` and ``MenuSubMenuRoot`` previously
   declared ``open_on_hover``, ``delay``, ``close_delay`` (moved to
   ``Menu.Trigger`` in 1.6.0) and ``loop`` (renamed to ``loopFocus``). Declared
   on Root, React silently dropped them -- the same dead-prop pattern as
   ``DialogRoot.dismissible``. The audit removes the relocated props from Root
   (re-exposing them on ``MenuTrigger``) and renames ``loop`` -> ``loop_focus``
   to match the 1.6.0 ``loopFocus`` prop.

2. ``menu`` destructive/inset prop plumbing. ``MenuItem`` (and
   ``MenuGroupLabel`` / ``MenuSubMenuTrigger``) declared
   ``data-[variant=destructive]`` / ``data-inset`` Tailwind selectors in their
   ``ClassNames`` but never converted ``variant``/``inset`` kwargs into
   ``data-variant``/``data-inset`` attributes. The sibling ``context_menu.py``
   implements that conversion; ``menu.py`` was refactored without it (commit
   755f3ed, PR #99), so ``menu.item("Delete", variant="destructive")`` silently
   folded the kwarg into an Emotion ``css`` style object and the destructive
   styling never applied. These tests pin the ``variant``/``inset`` ->
   ``data-*`` conversion (mirroring ``context_menu.py``'s pattern), guard the
   two wrappers against diverging again, and verify the shipped examples that
   manifested the bug now render the destructive affordance.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from reflex.components.component import Component  # noqa: E402

from app.www.library.examples import button_group_dropdown, menu_icons  # noqa: E402
from components.ui.context_menu import context_menu  # noqa: E402
from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.menu import (  # noqa: E402
    MenuRoot,
    MenuSubMenuRoot,
    MenuSubMenuTrigger,
    MenuTrigger,
    menu,
)
from tests.render_helpers import render_props  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(render_props(component))


def test_menu_root_no_longer_declares_dead_hover_props() -> None:
    props = MenuRoot.get_props()
    assert "open_on_hover" not in props
    assert "delay" not in props
    assert "close_delay" not in props
    assert "loop" not in props


def test_menu_root_loop_renamed_to_loop_focus() -> None:
    """``loop`` -> ``loop_focus`` (1.6.0 ``loopFocus``); both truth values
    round-trip as the camelCase top-level prop.
    """
    assert "loop_focus" in MenuRoot.get_props()
    assert "loopFocus:true" in _rendered(MenuRoot.create(loop_focus=True))
    assert "loopFocus:false" in _rendered(MenuRoot.create(loop_focus=False))
    assert "css:" not in _rendered(MenuRoot.create(loop_focus=True))


def test_menu_trigger_hover_props_forward_as_camel_case() -> None:
    """The relocated hover/delay props are re-exposed on ``Menu.Trigger`` and
    forward as the camelCase top-level props 1.6.0 ``MenuTriggerProps`` consumes.
    Asserting the forwarded form also confirms they are declared on the Trigger.
    """
    rendered = _rendered(
        MenuTrigger.create(open_on_hover=True, delay=100, close_delay=50),
    )
    assert "openOnHover:true" in rendered
    assert "delay:100" in rendered
    assert "closeDelay:50" in rendered


def test_menu_submenu_root_no_longer_declares_dead_hover_props() -> None:
    """``MenuSubMenuRoot`` mirrors ``MenuRoot``'s dead-prop set (same file, same
    1.6.0 audit) and must not keep the dead declarations after ``MenuRoot`` was
    fixed. ``loop`` became ``loop_focus``; the hover/delay props are
    Trigger-level only in 1.6.0.
    """
    props = MenuSubMenuRoot.get_props()
    assert "open_on_hover" not in props
    assert "delay" not in props
    assert "close_delay" not in props
    assert "loop" not in props
    assert "loop_focus" in props


def test_menu_submenu_trigger_hover_props_forward_as_camel_case() -> None:
    """1.6.0 consumes ``openOnHover``/``delay``/``closeDelay`` on
    ``Menu.SubmenuTrigger`` too, so the trio is re-exposed on
    ``MenuSubMenuTrigger`` (mirroring ``MenuTrigger``) and forwards as the
    camelCase top-level props, not into the inert ``css`` style dict.
    """
    assert "open_on_hover" in MenuSubMenuTrigger.get_props()
    assert "delay" in MenuSubMenuTrigger.get_props()
    assert "close_delay" in MenuSubMenuTrigger.get_props()

    rendered = _rendered(
        MenuSubMenuTrigger.create(open_on_hover=True, delay=100, close_delay=50),
    )
    assert "openOnHover:true" in rendered
    assert "delay:100" in rendered
    assert "closeDelay:50" in rendered
    assert "css:" not in rendered


def test_menu_submenu_root_no_longer_declares_dead_render() -> None:
    """``MenuSubMenuRoot`` is an element-less context-provider Root like
    ``MenuRoot`` (which declares no ``render_``), and 1.6.0's
    ``MenuSubmenuRootProps`` (``Omit<MenuRoot.Props, ...>``) declares no
    ``render`` -- so ``render_`` forwarded a dead prop React silently dropped.
    The audit removes it for parity with the other element-less Roots.
    """
    assert "render_" not in MenuSubMenuRoot.get_props()


def test_menu_item_converts_variant_to_data_attribute() -> None:
    item = menu.item("Delete", variant="destructive")

    assert item.custom_attrs["data-variant"] == "destructive"
    rendered = " ".join(render_props(item))
    assert '"data-variant":"destructive"' in rendered
    # The bug folded the kwarg into an Emotion css style object instead of
    # popping it; the "variant" key must not reach the rendered output.
    assert '["variant"]' not in rendered
    assert "css:" not in rendered


def test_menu_item_converts_inset_to_data_attribute() -> None:
    item = menu.item("Profile", inset=True)

    assert item.custom_attrs["data-inset"] is True
    rendered = " ".join(render_props(item))
    assert '"data-inset":true' in rendered
    assert '["inset"]' not in rendered


def test_menu_item_parity_with_context_menu_item() -> None:
    """``menu.item`` and ``context_menu.item`` share selector-based CSS and
    must share the same ``variant``/``inset`` -> ``data-*`` plumbing. The bug
    was caused by ``menu.py`` silently diverging from ``context_menu.py``.
    """
    m_item = menu.item("Delete", variant="destructive", inset=True)
    c_item = context_menu.item("Delete", variant="destructive", inset=True)

    assert m_item.custom_attrs["data-variant"] == c_item.custom_attrs["data-variant"]
    assert m_item.custom_attrs["data-inset"] == c_item.custom_attrs["data-inset"]


def test_menu_group_label_converts_inset_to_data_attribute() -> None:
    label = menu.group_label("Group", inset=True)

    assert label.custom_attrs["data-slot"] == "menu-group-label"
    assert label.custom_attrs["data-inset"] is True
    rendered = " ".join(render_props(label))
    assert '"data-inset":true' in rendered
    assert '["inset"]' not in rendered


def test_menu_submenu_trigger_converts_inset_to_data_attribute() -> None:
    trigger = menu.submenu_trigger("More", inset=True)

    assert trigger.custom_attrs["data-slot"] == "menu-submenu-trigger"
    assert trigger.custom_attrs["data-inset"] is True
    rendered = " ".join(render_props(trigger))
    assert '"data-inset":true' in rendered
    assert '["inset"]' not in rendered


def test_menu_submenu_trigger_converts_variant_to_data_attribute() -> None:
    trigger = menu.submenu_trigger("Danger", variant="destructive")

    assert trigger.custom_attrs["data-variant"] == "destructive"
    rendered = " ".join(render_props(trigger))
    assert '"data-variant":"destructive"' in rendered
    # The bug folded the kwarg into an Emotion css style object instead of
    # popping it; the "variant" key must not reach the rendered output.
    assert '["variant"]' not in rendered
    assert "css:" not in rendered


def _walk(component: Component) -> Iterator[Component]:
    yield component
    for child in component.children:
        if isinstance(child, Component):
            yield from _walk(child)


def test_menu_icons_example_renders_destructive_item() -> None:
    """The shipped ``menu_icons`` example calls ``menu.item(...,
    variant="destructive")`` for its "Log out" action -- that destructive
    affordance must reach the DOM as a ``data-variant`` attribute.
    """
    destructive = [
        c
        for c in _walk(menu_icons.menu_icons())
        if c.custom_attrs.get("data-variant") == "destructive"
    ]

    assert len(destructive) == 1
    assert type(destructive[0]).__name__ == "MenuItem"


def test_button_group_dropdown_example_renders_destructive_item() -> None:
    """The shipped ``button_group_dropdown`` example calls ``menu.item(
    "Delete Conversation", variant="destructive")`` -- that destructive
    affordance must reach the DOM as a ``data-variant`` attribute.
    """
    destructive = [
        c
        for c in _walk(button_group_dropdown.button_group_dropdown())
        if c.custom_attrs.get("data-variant") == "destructive"
    ]

    assert len(destructive) == 1
    assert type(destructive[0]).__name__ == "MenuItem"
