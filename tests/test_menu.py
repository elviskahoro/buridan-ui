"""Regression tests for ``menu`` destructive/inset prop plumbing.

``MenuItem`` (and ``MenuGroupLabel`` / ``MenuSubMenuTrigger``) declared
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

from reflex.components.component import Component

from app.www.library.examples import button_group_dropdown, menu_icons
from components.ui.context_menu import context_menu
from components.ui.menu import menu


def test_menu_item_converts_variant_to_data_attribute() -> None:
    item = menu.item("Delete", variant="destructive")

    assert item.custom_attrs["data-variant"] == "destructive"
    rendered = " ".join(item.render()["props"])
    assert '"data-variant":"destructive"' in rendered
    # The bug folded the kwarg into an Emotion css style object instead of
    # popping it; the "variant" key must not reach the rendered output.
    assert '["variant"]' not in rendered
    assert "css:" not in rendered


def test_menu_item_converts_inset_to_data_attribute() -> None:
    item = menu.item("Profile", inset=True)

    assert item.custom_attrs["data-inset"] is True
    rendered = " ".join(item.render()["props"])
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
    rendered = " ".join(label.render()["props"])
    assert '"data-inset":true' in rendered
    assert '["inset"]' not in rendered


def test_menu_submenu_trigger_converts_inset_to_data_attribute() -> None:
    trigger = menu.submenu_trigger("More", inset=True)

    assert trigger.custom_attrs["data-slot"] == "menu-submenu-trigger"
    assert trigger.custom_attrs["data-inset"] is True
    rendered = " ".join(trigger.render()["props"])
    assert '"data-inset":true' in rendered
    assert '["inset"]' not in rendered


def test_menu_submenu_trigger_converts_variant_to_data_attribute() -> None:
    trigger = menu.submenu_trigger("Danger", variant="destructive")

    assert trigger.custom_attrs["data-variant"] == "destructive"
    rendered = " ".join(trigger.render()["props"])
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
