import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.context_menu import (  # noqa: E402
    ClassNames,
    ContextMenuRoot,
    ContextMenuShortcut,
    ContextMenuSubmenuRoot,
    ContextMenuSubmenuTrigger,
)
from components.ui.core import BaseUIComponent  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_context_menu_shortcut_uses_default_classes() -> None:
    shortcut = ContextMenuShortcut.create("Ctrl+C")

    assert ClassNames.SHORTCUT in str(shortcut.class_name)


def test_context_menu_shortcut_merges_custom_class_name() -> None:
    shortcut = ContextMenuShortcut.create("Ctrl+C", class_name="custom-shortcut")

    assert ClassNames.SHORTCUT in str(shortcut.class_name)
    assert "custom-shortcut" in str(shortcut.class_name)


def test_context_menu_shortcut_unstyled_omits_default_classes() -> None:
    shortcut = ContextMenuShortcut.create("Ctrl+C", unstyled=True)

    assert str(shortcut.class_name) == ""


def test_context_menu_shortcut_unstyled_keeps_custom_class_name() -> None:
    shortcut = ContextMenuShortcut.create(
        "Ctrl+C",
        class_name="custom-shortcut",
        unstyled=True,
    )

    assert str(shortcut.class_name) == "custom-shortcut"


# ---------------------------------------------------------------------------
# Base UI 1.6.0 dead-prop audit (parity with MenuRoot/MenuSubMenuRoot)
# ---------------------------------------------------------------------------


def test_context_menu_root_loop_renamed_to_loop_focus() -> None:
    """``ContextMenuRoot.loop`` was dead in 1.6.0 (``ContextMenu.Root`` inherits
    ``loopFocus``); renamed to ``loop_focus`` to match the runtime, mirroring
    ``MenuRoot``.
    """
    props = ContextMenuRoot.get_props()
    assert "loop" not in props
    assert "loop_focus" in props
    assert "loopFocus:true" in _rendered(ContextMenuRoot.create(loop_focus=True))
    assert "loopFocus:false" in _rendered(ContextMenuRoot.create(loop_focus=False))
    assert "css:" not in _rendered(ContextMenuRoot.create(loop_focus=True))


def test_context_menu_submenu_root_no_longer_declares_dead_hover_props() -> None:
    """``ContextMenuSubmenuRoot`` declared ``open_on_hover``/``delay``/
    ``close_delay`` (dead on ``MenuSubmenuRootProps`` in 1.6.0) and ``loop``
    (renamed). The hover/delay trio is re-exposed on
    ``ContextMenuSubmenuTrigger`` (see below); ``loop`` became ``loop_focus``.
    """
    props = ContextMenuSubmenuRoot.get_props()
    assert "open_on_hover" not in props
    assert "delay" not in props
    assert "close_delay" not in props
    assert "loop" not in props
    assert "loop_focus" in props


def test_context_menu_submenu_trigger_hover_props_forward_as_camel_case() -> None:
    """1.6.0 consumes ``openOnHover``/``delay``/``closeDelay`` on
    ``Menu.SubmenuTrigger`` (``ContextMenuSubmenuTriggerProps`` aliases it), so
    the trio is re-exposed on ``ContextMenuSubmenuTrigger`` and forwards as the
    camelCase top-level props, not into the inert ``css`` style dict.
    """
    assert "open_on_hover" in ContextMenuSubmenuTrigger.get_props()
    assert "delay" in ContextMenuSubmenuTrigger.get_props()
    assert "close_delay" in ContextMenuSubmenuTrigger.get_props()

    rendered = _rendered(
        ContextMenuSubmenuTrigger.create(open_on_hover=True, delay=100, close_delay=50),
    )
    assert "openOnHover:true" in rendered
    assert "delay:100" in rendered
    assert "closeDelay:50" in rendered
    assert "css:" not in rendered
