"""Regression tests for the ``input_group`` controls' ``unstyled`` contract.

``InputGroupInput``, ``InputGroupTextarea``, and ``InputGroupButton`` used to
pre-bake their default classes into ``props["class_name"]`` via ``cn()``
*before* delegating to ``input()``/``textarea()``/``button()``, so
``CoreComponent.set_class_name``'s ``unstyled=True`` branch (``core.py``) was
unreachable for them: the wrapper classes were already merged into what the
inner component treated as "the caller's class_name". ``input_group.root``,
``.addon``, and ``.text`` already routed through ``set_class_name`` correctly
(see https://github.com/elviskahoro/buridan-ui/issues/167).

The fix routes the wrapper-level defaults through ``cls.set_class_name(...)``
and re-forwards ``unstyled`` into the inner ``input()``/``textarea()``/
``button()`` call so each layer independently honors the escape hatch.

Note: ``Button.create`` (``components/ui/button.py``) does not itself
consult ``unstyled`` when merging its own default/variant/size classes -
that is a separate, pre-existing bug in ``button.py`` and is out of scope
here. The button tests below only assert that the ``input_group.button``
*wrapper* classes honor ``unstyled``.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx  # noqa: E402

from components.ui.input import ClassNames as InputClassNames  # noqa: E402
from components.ui.input_group import (  # noqa: E402
    ClassNames,
    InputGroupButton,
    InputGroupInput,
    InputGroupTextarea,
)
from components.ui.textarea import ClassNames as TextareaClassNames  # noqa: E402
from tests.render_helpers import render_props


class _UnstyledState(rx.State):  # pyright: ignore[reportUntypedBaseClass]
    """State exposing a boolean Var for the dynamic ``unstyled`` escape hatch."""

    flag: bool = False


# ---------------------------------------------------------------------------
# InputGroupInput
# ---------------------------------------------------------------------------


def test_input_group_input_uses_default_classes() -> None:
    control = InputGroupInput.create()
    class_name = str(control.class_name)

    assert ClassNames.CONTROL_INPUT in class_name
    assert InputClassNames.INPUT in class_name


def test_input_group_input_merges_custom_class_name() -> None:
    control = InputGroupInput.create(class_name="custom-input")
    class_name = str(control.class_name)

    assert ClassNames.CONTROL_INPUT in class_name
    assert InputClassNames.INPUT in class_name
    assert "custom-input" in class_name


def test_input_group_input_unstyled_keeps_only_custom_class() -> None:
    control = InputGroupInput.create(class_name="custom-input", unstyled=True)

    assert str(control.class_name) == "custom-input"


def test_input_group_input_unstyled_without_custom_class_is_empty() -> None:
    control = InputGroupInput.create(unstyled=True)

    assert str(control.class_name) == ""


def test_input_group_input_unstyled_not_rendered_to_dom() -> None:
    control = InputGroupInput.create(class_name="custom-input", unstyled=True)
    rendered_props = " ".join(render_props(control))

    assert "unstyled" not in rendered_props


def test_input_group_input_var_unstyled_toggles_classes_dynamically() -> None:
    control = InputGroupInput.create(
        class_name="custom-input",
        unstyled=_UnstyledState.flag,
    )
    class_name = str(control.class_name)

    # The class_name is gated on the Var via a ternary (rx.cond), not stripped.
    assert "?" in class_name
    assert "custom-input" in class_name
    assert ClassNames.CONTROL_INPUT in class_name
    assert InputClassNames.INPUT in class_name


def test_input_group_input_defaults_type_and_data_slot() -> None:
    control = InputGroupInput.create()
    rendered_props = " ".join(render_props(control))

    assert 'type:"text"' in rendered_props
    assert '"data-slot":"input-group-control"' in rendered_props


# ---------------------------------------------------------------------------
# InputGroupTextarea
# ---------------------------------------------------------------------------


def test_input_group_textarea_uses_default_classes() -> None:
    control = InputGroupTextarea.create()
    class_name = str(control.class_name)

    assert ClassNames.CONTROL_TEXTAREA in class_name
    assert TextareaClassNames.ROOT in class_name


def test_input_group_textarea_merges_custom_class_name() -> None:
    control = InputGroupTextarea.create(class_name="custom-textarea")
    class_name = str(control.class_name)

    assert ClassNames.CONTROL_TEXTAREA in class_name
    assert TextareaClassNames.ROOT in class_name
    assert "custom-textarea" in class_name


def test_input_group_textarea_unstyled_keeps_only_custom_class() -> None:
    control = InputGroupTextarea.create(class_name="custom-textarea", unstyled=True)

    assert str(control.class_name) == "custom-textarea"


def test_input_group_textarea_unstyled_without_custom_class_is_empty() -> None:
    control = InputGroupTextarea.create(unstyled=True)

    assert str(control.class_name) == ""


def test_input_group_textarea_unstyled_not_rendered_to_dom() -> None:
    control = InputGroupTextarea.create(class_name="custom-textarea", unstyled=True)
    rendered_props = " ".join(render_props(control))

    assert "unstyled" not in rendered_props


def test_input_group_textarea_defaults_data_slot() -> None:
    control = InputGroupTextarea.create()
    rendered_props = " ".join(render_props(control))

    assert '"data-slot":"input-group-control"' in rendered_props


# ---------------------------------------------------------------------------
# InputGroupButton
# ---------------------------------------------------------------------------

_WRAPPER_MARKER = "shadow-none"
_SIZE_XS_MARKER = "rounded-[calc(var(--radius)-3px)]"
_BUTTON_DEFAULT_MARKER = "group/button"


def test_input_group_button_uses_default_classes() -> None:
    control = InputGroupButton.create("Send")
    class_name = str(control.class_name)

    assert _WRAPPER_MARKER in class_name
    assert _SIZE_XS_MARKER in class_name
    # Button's own defaults (components/ui/button.py) still merge in; the
    # input_group wrapper is not responsible for those.
    assert _BUTTON_DEFAULT_MARKER in class_name


def test_input_group_button_merges_custom_class_name() -> None:
    control = InputGroupButton.create("Send", class_name="custom-btn")
    class_name = str(control.class_name)

    assert _WRAPPER_MARKER in class_name
    assert "custom-btn" in class_name


def test_input_group_button_unstyled_omits_wrapper_defaults() -> None:
    """The wrapper-level defaults (this file's bug) honor ``unstyled``.

    ``Button.create`` itself does not yet consult ``unstyled`` when merging
    its own ``DEFAULT_CLASS_NAME``/variant/size classes (``components/ui/
    button.py``) - that is a separate, pre-existing bug and out of scope for
    this fix, so ``_BUTTON_DEFAULT_MARKER`` is still expected here.
    """
    control = InputGroupButton.create("Send", class_name="custom-btn", unstyled=True)
    class_name = str(control.class_name)

    assert "custom-btn" in class_name
    assert _WRAPPER_MARKER not in class_name
    assert _SIZE_XS_MARKER not in class_name
    assert _BUTTON_DEFAULT_MARKER in class_name


def test_input_group_button_unstyled_not_rendered_to_dom() -> None:
    control = InputGroupButton.create("Send", class_name="custom-btn", unstyled=True)
    rendered_props = " ".join(render_props(control))

    assert "unstyled" not in rendered_props


def test_input_group_button_defaults_type_variant_and_size() -> None:
    control = InputGroupButton.create("Send")
    rendered_props = " ".join(render_props(control))

    assert 'type:"button"' in rendered_props
    assert '"data-size":"xs"' in rendered_props


def test_input_group_button_preserves_explicit_size() -> None:
    control = InputGroupButton.create("Send", size="icon-sm")
    class_name = str(control.class_name)
    rendered_props = " ".join(render_props(control))

    assert '"data-size":"icon-sm"' in rendered_props
    assert "size-8" in class_name
