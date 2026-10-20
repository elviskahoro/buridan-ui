# ruff: noqa: INP001
"""Regression tests for the ``collision_avoidance`` prop on Base UI positioner wrappers.

``@base-ui/react@1.6.0`` defines ``collisionAvoidance`` as a ``CollisionAvoidance``
object (``{side?, align?, fallbackAxisSide?}``), not a string — it reads
``collisionAvoidance.side`` / ``.align`` / ``.fallbackAxisSide`` directly, and a
bare string has no ``.side`` property so every field silently falls back to the
default (and may even throw when used in a ``'side' in collisionAvoidance`` check
on a context menu positioner).

Before the fix:
- ``ContextMenuPositioner`` / ``MenuPositioner`` typed ``collision_avoidance`` as
  ``Var[Literal["flip", "shift", "auto"]]`` — a literal whose values do not exist
  in Base UI at all. Passing the object form raised ``TypeError`` at
  component-creation time; passing a string compiled to a dead
  ``collisionAvoidance:"flip"`` that the library cannot consume.
- ``SelectPositioner`` / ``PopoverPositioner`` typed it as ``Var[str]``, which
  also rejected the object form.
- ``TooltipPositioner`` already used ``Var[str | dict[str, str]]``.

The fix widens all four broken positioners to ``Var[str | dict[str, str]]``
(and restores ``bool`` to ``MenuPositioner``'s union, since it previously
accepted ``Var[bool | LiteralCollisionAvoidance]``) and removes the dead
``LiteralCollisionAvoidance`` alias from ``context_menu`` and ``menu``. These
tests pin that contract across all five positioner wrappers
(``TooltipPositioner`` is included as the canonical reference).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pytest  # noqa: E402

from components.ui.context_menu import ContextMenuPositioner  # noqa: E402
from components.ui.menu import MenuPositioner  # noqa: E402
from components.ui.popover import PopoverPositioner  # noqa: E402
from components.ui.select import SelectPositioner  # noqa: E402
from components.ui.tooltip import TooltipPositioner  # noqa: E402

POSITIONER_CLASSES = [
    ContextMenuPositioner,
    MenuPositioner,
    SelectPositioner,
    PopoverPositioner,
    TooltipPositioner,
]


@pytest.mark.parametrize(
    "positioner_cls",
    POSITIONER_CLASSES,
    ids=lambda cls: cls.__name__,
)
def test_collision_avoidance_accepts_object_form(positioner_cls: type) -> None:
    """The dict form ``{'side': 'none'}`` must not raise at component-creation time.

    Regression for the original ``TypeError: Invalid var passed for prop
    <Name>.collision_avoidance, ... got value {'side': 'none'} of type
    collections.abc.Mapping[str, str]`` raised when the prop was typed as
    ``Var[Literal[...]]`` or ``Var[str]``.
    """
    component = positioner_cls.create(collision_avoidance={"side": "none"})

    rendered_props = " ".join(component.render()["props"])
    assert "collisionAvoidance:" in rendered_props


@pytest.mark.parametrize(
    "positioner_cls",
    POSITIONER_CLASSES,
    ids=lambda cls: cls.__name__,
)
def test_collision_avoidance_dict_renders_as_js_object(positioner_cls: type) -> None:
    """The dict form must compile to a JS object literal, not a bare JS string.

    Regression for the silent-dead-prop side of the bug: when the prop accepted
    strings (``Literal["flip", ...]`` or ``Var[str]``), a value like ``"flip"``
    compiled to ``collisionAvoidance:"flip"`` — a bare JS string the library reads
    as ``collisionAvoidance.side`` (which is ``undefined``) and therefore silently
    ignores. The dict form must instead emit a JS object the library can consume.
    """
    component = positioner_cls.create(collision_avoidance={"side": "none"})
    rendered_props = " ".join(component.render()["props"])

    # The serialized form is `collisionAvoidance:({ ["side"] : "none" })` — the
    # leading `(` and quoted `["side"]` key prove an object literal was emitted.
    assert "collisionAvoidance:(" in rendered_props
    assert '["side"]' in rendered_props
    assert '"none"' in rendered_props
    # And the value must NOT be forwarded as a bare string like
    # `collisionAvoidance:"flip"` — that form is what the library cannot consume.
    assert 'collisionAvoidance:"' not in rendered_props


@pytest.mark.parametrize(
    "positioner_cls",
    POSITIONER_CLASSES,
    ids=lambda cls: cls.__name__,
)
def test_collision_avoidance_accepts_full_collision_avoidance_object(
    positioner_cls: type,
) -> None:
    """A complete ``CollisionAvoidance`` object with all three keys is accepted.

    Base UI's ``CollisionAvoidance`` type allows ``side``, ``align``, and
    ``fallbackAxisSide``; each key must survive the round-trip into the rendered
    JS object so the library can read it via ``collisionAvoidance.<key>``.
    """
    component = positioner_cls.create(
        collision_avoidance={
            "side": "flip",
            "align": "shift",
            "fallbackAxisSide": "none",
        },
    )
    rendered_props = " ".join(component.render()["props"])

    assert '["side"]' in rendered_props
    assert '["align"]' in rendered_props
    assert '["fallbackAxisSide"]' in rendered_props
    assert '"flip"' in rendered_props
    assert '"shift"' in rendered_props
    assert '"none"' in rendered_props


@pytest.mark.parametrize(
    "positioner_cls",
    POSITIONER_CLASSES,
    ids=lambda cls: cls.__name__,
)
def test_collision_avoidance_string_form_still_accepted(positioner_cls: type) -> None:
    """The ``str`` half of ``Var[str | dict[str, str]]`` remains accepted.

    The fix widens the type rather than narrowing it; consumers that previously
    passed a plain string to ``SelectPositioner`` / ``PopoverPositioner`` (which
    were typed ``Var[str]``) must continue to compile without error.
    """
    component = positioner_cls.create(collision_avoidance="flip")
    rendered_props = " ".join(component.render()["props"])

    assert 'collisionAvoidance:"flip"' in rendered_props


@pytest.mark.parametrize(
    "positioner_cls",
    [MenuPositioner],
    ids=lambda cls: cls.__name__,
)
def test_collision_avoidance_bool_form_still_accepted_on_menu(
    positioner_cls: type,
) -> None:
    """``MenuPositioner`` previously typed ``collision_avoidance`` as
    ``Var[bool | LiteralCollisionAvoidance]``, so ``collision_avoidance=True``
    compiled. The widened ``Var[str | dict[str, str]]`` form would have rejected
    that caller with a ``TypeError``; restoring ``bool`` to the union keeps the
    pre-fix ``True`` form accepted (it remains a dead prop at runtime, like any
    bare non-object value, but it must not raise at component-creation time).
    """
    component = positioner_cls.create(collision_avoidance=True)
    rendered_props = " ".join(component.render()["props"])

    # The bool is forwarded as a literal (lowercased by the serializer) rather
    # than raising a TypeError, matching the pre-fix behavior where
    # ``Var[bool | ...]`` accepted it.
    assert "collisionAvoidance:true" in rendered_props


@pytest.mark.parametrize(
    "module_name",
    ["components.ui.context_menu", "components.ui.menu"],
    ids=lambda name: name.split(".")[-1],
)
def test_literal_collision_avoidance_alias_removed(module_name: str) -> None:
    """The dead ``LiteralCollisionAvoidance`` alias has been removed.

    ``LiteralCollisionAvoidance = Literal["flip", "shift", "auto"]`` referenced
    values that do not exist anywhere in ``@base-ui/react`` (there is no
    ``"auto"`` mode, and the library does not accept a string in the first
    place). With ``collision_avoidance`` retyped to ``Var[str | dict[str, str]]``,
    the alias has no remaining users and must be removed so it does not mislead
    consumers into thinking the literal values are valid.
    """
    module = sys.modules[module_name]

    assert not hasattr(module, "LiteralCollisionAvoidance"), (
        f"{module_name} should no longer define the dead LiteralCollisionAvoidance "
        "alias; collision_avoidance is now typed as "
        "Var[str | dict[str, str]] (with bool also accepted on MenuPositioner) ."
    )
