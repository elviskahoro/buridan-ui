"""Regression tests for the Menu wrapper's audit of dead Base UI 1.6.0 props.

``MenuRoot`` and ``MenuSubMenuRoot`` previously declared ``open_on_hover``,
``delay``, ``close_delay`` (moved to ``Menu.Trigger`` in 1.6.0) and ``loop``
(renamed to ``loopFocus``). Declared on Root, React silently dropped them -- the
same dead-prop pattern as ``DialogRoot.dismissible``. The audit removes the
relocated props from Root (re-exposing them on ``MenuTrigger``) and renames
``loop`` -> ``loop_focus`` to match the 1.6.0 ``loopFocus`` prop.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.menu import (  # noqa: E402
    MenuRoot,
    MenuSubMenuRoot,
    MenuSubMenuTrigger,
    MenuTrigger,
)


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


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
