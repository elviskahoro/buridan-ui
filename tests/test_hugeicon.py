"""Regression tests for ``components.icons.hugeicon.HugeIcon`` / ``hi``.

``hi()`` must reject a dynamic ``Var`` (e.g. ``hi(state.icon)``) or a non-``str``
expression such as ``rx.cond(...)`` passed as the icon, since the per-icon
``@hugeicons/core-free-icons`` import the design depends on can only be emitted
for a compile-time string literal. Without this guard the ``icon`` prop is
omitted and ``@hugeicons/react``'s ``HugeiconsIcon`` crashes the page at render
with ``TypeError: undefined is not iterable``.
"""

import pytest
import reflex as rx
from reflex.vars.base import Var

from components.icons.hugeicon import hi


def test_hugeicon_rejects_var_positional_child() -> None:
    with pytest.raises(TypeError) as exc_info:
        hi(Var.create("Tick02Icon"), class_name="size-4")

    message = str(exc_info.value)
    assert "hi()" in message
    assert "LiteralStringVar" in message


def test_hugeicon_rejects_icon_var_kwarg() -> None:
    with pytest.raises(TypeError) as exc_info:
        hi(icon=Var.create("Tick02Icon"))

    message = str(exc_info.value)
    assert "hi()" in message
    assert "'icon'" in message
    assert "LiteralStringVar" in message


def test_hugeicon_rejects_alt_icon_var_kwarg() -> None:
    with pytest.raises(TypeError) as exc_info:
        hi("Tick02Icon", alt_icon=Var.create("HomeIcon"))

    message = str(exc_info.value)
    assert "hi()" in message
    assert "'alt_icon'" in message
    assert "LiteralStringVar" in message


def test_hugeicon_rejects_non_str_positional_child() -> None:
    """A dynamic expression such as rx.cond(...) returns a Fragment, not a str."""
    with pytest.raises(TypeError) as exc_info:
        hi(rx.cond(True, hi("Tick02Icon"), hi("HomeIcon")))

    assert "Fragment" in str(exc_info.value)


def test_hugeicon_documented_workaround_cond_over_whole_components() -> None:
    """Switching whole hi('...') components via rx.cond is the supported pattern."""
    fragment = rx.cond(True, hi("Tick02Icon"), hi("HomeIcon"))

    imports = set(fragment._get_all_imports())
    assert "@hugeicons/core-free-icons@4.2.1" in imports
    assert "@hugeicons/react@1.1.6" in imports
