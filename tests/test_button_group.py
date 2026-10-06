"""Regression tests for ``button_group`` orientation handling.

``ButtonGroupRoot`` selects a horizontal vs. vertical Tailwind variant from its
``orientation`` prop. The variant must be chosen with a Var-aware branch
(``cond``) rather than a plain-Python ternary, so binding ``orientation`` to a
Reflex state ``Var`` (the standard reactivity pattern) does not raise
``VarTypeError``. These tests guard against reintroducing a Python-bool branch
on the prop and against silently regressing reactivity or Var prop-forwarding.

Per the established convention (see ``tests/test_context_menu.py`` and
``tests/test_collapsible.py``), ``cn()`` resolves to a deferred reflex ``Var``
whose ``str()`` form embeds every literal input, so assertions are made against
``str(component.class_name)`` and ``custom_attrs``.
"""

import sys
from pathlib import Path
from typing import Literal

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx
from reflex.vars.base import Var

from components.ui.button_group import ButtonGroupRoot, ClassNames, button_group


class _State(rx.State):
    layout: Literal["horizontal", "vertical"] = "vertical"


def test_button_group_root_accepts_literal_orientation() -> None:
    # The existing literal happy path must keep working.
    assert button_group.root(orientation="horizontal") is not None
    assert button_group.root(orientation="vertical") is not None


def test_button_group_root_accepts_var_orientation() -> None:
    # Binding `orientation` to state is the standard Reflex reactivity pattern;
    # it must not raise VarTypeError ("Cannot convert Var ... to bool ...").
    assert button_group.root(orientation=_State.layout) is not None
    assert ButtonGroupRoot.create(orientation=_State.layout) is not None


def test_var_orientation_emits_reactive_ternary() -> None:
    # The Var-bound class must be a genuinely reactive expression (not a static
    # literal coerced out of the Var), with both branches available to switch.
    root = button_group.root(orientation=_State.layout)

    class_name = str(root.class_name)
    assert ClassNames.BASE_GROUP in class_name
    assert "layout" in class_name
    assert '=== "horizontal"' in class_name
    assert ClassNames.HORIZONTAL in class_name
    assert ClassNames.VERTICAL in class_name


def test_root_forwards_var_data_orientation() -> None:
    # A Var-bound orientation must forward a Var to `data-orientation`, not a
    # coerced bool/string that would silently break the attribute's reactivity.
    data_orientation = button_group.root(orientation=_State.layout).custom_attrs[
        "data-orientation"
    ]
    assert isinstance(data_orientation, Var)
    assert "layout" in str(data_orientation)
