# pyright: reportUnknownMemberType=false
import sys
from pathlib import Path

import reflex as rx

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.context_menu import (  # noqa: E402
    ClassNames,
    ContextMenuCheckboxItem,
    ContextMenuCheckboxItemIndicator,
    ContextMenuGroupLabel,
    ContextMenuItem,
    ContextMenuRadioItem,
    ContextMenuRadioItemIndicator,
    ContextMenuRoot,
    ContextMenuShortcut,
    ContextMenuSubmenuRoot,
    ContextMenuSubmenuTrigger,
)
from components.ui.core import BaseUIComponent  # noqa: E402


class _ContextMenuState(rx.State):  # pyright: ignore[reportUntypedBaseClass]
    """State exposing Vars for the dynamic ``inset``/``variant`` escape hatch."""

    is_inset: bool = False
    item_variant: str = "default"


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


def test_context_menu_submenu_root_no_longer_declares_dead_render() -> None:
    """``ContextMenuSubmenuRoot`` is an element-less context-provider Root like
    ``ContextMenuRoot`` (which declares no ``render_``), and 1.6.0's
    ``ContextMenuSubmenuRootProps`` (= ``MenuSubmenuRootProps``) declares no
    ``render`` -- so ``render_`` forwarded a dead prop React silently dropped.
    The audit removes it for parity with the other element-less Roots.
    """
    assert "render_" not in ContextMenuSubmenuRoot.get_props()


# ---------------------------------------------------------------------------
# inset/variant must accept state Vars, not just literals (#83)
# ---------------------------------------------------------------------------


def test_context_menu_item_inset_and_variant_accept_state_vars() -> None:
    """``if props.get("inset"):`` / ``if props.get("variant"):`` called ``bool()``
    on a ``Var``, which raises ``VarTypeError`` at app-definition time. The fix
    switches to presence checks (``"inset" in props``) so a bound state ``Var``
    is forwarded instead of crashing construction.
    """
    item = ContextMenuItem.create(
        "Delete",
        inset=_ContextMenuState.is_inset,
        variant=_ContextMenuState.item_variant,
    )
    rendered_props = " ".join(item.render()["props"])

    assert '"data-inset":' in rendered_props
    assert '"data-variant":' in rendered_props


def test_context_menu_item_inset_and_variant_still_accept_literals() -> None:
    item = ContextMenuItem.create("Delete", inset=True, variant="destructive")
    rendered_props = " ".join(item.render()["props"])

    assert '"data-inset":true' in rendered_props
    assert '"data-variant":"destructive"' in rendered_props


def test_context_menu_item_inset_false_does_not_trigger_padding_selector() -> None:
    """``"inset" in props`` forwards ``inset=False`` as ``data-inset="false"``.
    Since ``data-inset:pl-7`` is a bare presence selector (``&[data-inset]``),
    it would match that attribute regardless of its value. ``ClassNames.ITEM``
    must use the value-based ``data-[inset=true]:pl-7`` selector so a falsy
    ``inset`` never applies the padding.
    """
    for class_names in (
        ClassNames.ITEM,
        ClassNames.GROUP_LABEL,
        ClassNames.RADIO_ITEM,
        ClassNames.CHECKBOX_ITEM,
        ClassNames.SUBMENU_TRIGGER,
    ):
        assert "data-inset:pl-7" not in class_names
        assert "data-[inset=true]:pl-7" in class_names

    item = ContextMenuItem.create("Delete", inset=False)
    rendered_props = " ".join(item.render()["props"])

    assert '"data-inset":false' in rendered_props


def test_context_menu_group_label_inset_accepts_state_var() -> None:
    label = ContextMenuGroupLabel.create("Actions", inset=_ContextMenuState.is_inset)

    assert '"data-inset":' in " ".join(label.render()["props"])


def test_context_menu_radio_item_inset_accepts_state_var() -> None:
    radio_item = ContextMenuRadioItem.create(
        "Option",
        value="a",
        inset=_ContextMenuState.is_inset,
    )

    assert '"data-inset":' in " ".join(radio_item.render()["props"])


def test_context_menu_checkbox_item_inset_accepts_state_var() -> None:
    checkbox_item = ContextMenuCheckboxItem.create(
        "Option",
        inset=_ContextMenuState.is_inset,
    )

    assert '"data-inset":' in " ".join(checkbox_item.render()["props"])


def test_context_menu_submenu_trigger_inset_accepts_state_var() -> None:
    sub_trigger = ContextMenuSubmenuTrigger.create(
        "More",
        inset=_ContextMenuState.is_inset,
    )

    assert '"data-inset":' in " ".join(sub_trigger.render()["props"])


# ---------------------------------------------------------------------------
# bare checkbox/radio indicators must render a default tick (#221)
# ---------------------------------------------------------------------------


def test_context_menu_radio_item_indicator_injects_default_tick_when_bare() -> None:
    indicator = ContextMenuRadioItemIndicator.create()

    assert len(indicator.children) == 1


def test_context_menu_radio_item_indicator_preserves_custom_children() -> None:
    custom_icon = rx.el.span("custom")
    indicator = ContextMenuRadioItemIndicator.create(custom_icon)

    assert len(indicator.children) == 1
    assert indicator.children[0] is custom_icon


def test_context_menu_checkbox_item_indicator_injects_default_tick_when_bare() -> None:
    indicator = ContextMenuCheckboxItemIndicator.create()

    assert len(indicator.children) == 1


def test_context_menu_checkbox_item_indicator_preserves_custom_children() -> None:
    custom_icon = rx.el.span("custom")
    indicator = ContextMenuCheckboxItemIndicator.create(custom_icon)

    assert len(indicator.children) == 1
    assert indicator.children[0] is custom_icon
