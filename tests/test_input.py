import json
import sys
from pathlib import Path
from typing import Any, cast

import reflex as rx
from reflex.vars.base import Var

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.input import (
    BaseInput,
    CheckboxInput,
    ClassNames,
    InputComponent,
    ValueNumberInput,
)


class _InputTestState(rx.State):
    v: int = 0
    b: bool = False

    def set_v(self, v: Any) -> None:
        self.v = v

    def set_b(self, b: Any) -> None:
        self.b = b


def _capture_input_props(monkeypatch) -> dict:
    """Capture props passed to the underlying Reflex input component."""
    captured = {}

    def create(cls, *children, **props):
        captured.update(props)
        return props

    monkeypatch.setattr(BaseInput, "create", classmethod(create))
    return captured


def _on_change_arg(comp) -> Var:
    spec = comp.event_triggers["on_change"].events[0]
    return spec.args[0][1]


def _capture_typed_create_props(monkeypatch, typed_cls: type) -> dict:
    captured: dict = {}

    def create(cls, *children, **props):
        captured.update(props)
        return props

    monkeypatch.setattr(typed_cls, "create", classmethod(create))
    return captured


def test_input_uses_default_classes(monkeypatch) -> None:
    captured = _capture_input_props(monkeypatch)

    InputComponent.create()

    assert ClassNames.INPUT in str(captured["class_name"])


def test_input_merges_custom_classes_with_defaults(monkeypatch) -> None:
    captured = _capture_input_props(monkeypatch)

    InputComponent.create(class_name="custom-input")

    class_name = str(captured["class_name"])
    assert ClassNames.INPUT in class_name
    assert "custom-input" in class_name


def test_input_unstyled_keeps_custom_classes_without_defaults(monkeypatch) -> None:
    captured = _capture_input_props(monkeypatch)

    InputComponent.create(class_name="custom-input", unstyled=True)

    assert captured["class_name"] == "custom-input"
    assert "unstyled" not in captured


def test_input_defaults_type_and_data_slot(monkeypatch) -> None:
    captured = _capture_input_props(monkeypatch)

    InputComponent.create()

    assert captured["type"] == "text"
    assert captured["data_slot"] == "input"


def test_input_preserves_explicit_type_and_data_slot(monkeypatch) -> None:
    captured = _capture_input_props(monkeypatch)

    InputComponent.create(type="email", data_slot="custom-input")

    assert captured["type"] == "email"
    assert captured["data_slot"] == "custom-input"


def test_checkbox_input_dispatches_with_boolean_payload() -> None:
    comp = InputComponent.create(type="checkbox", on_change=_InputTestState.set_b)

    assert isinstance(comp, CheckboxInput)

    arg = _on_change_arg(comp)
    assert type(arg).__name__ == "BooleanCastedVar"
    assert arg._var_type is bool


def test_number_input_dispatches_with_number_payload() -> None:
    comp = InputComponent.create(type="number", on_change=_InputTestState.set_v)

    assert isinstance(comp, ValueNumberInput)

    arg = _on_change_arg(comp)
    assert type(arg).__name__ == "NumberCastedVar"
    assert arg._var_type is float


def test_range_input_dispatches_with_number_payload() -> None:
    comp = InputComponent.create(type="range", on_change=_InputTestState.set_v)

    assert isinstance(comp, ValueNumberInput)

    arg = _on_change_arg(comp)
    assert type(arg).__name__ == "NumberCastedVar"
    assert arg._var_type is float


def test_non_typed_inputs_stay_input_component_with_string_payload() -> None:
    # The fix must only reroute checkbox/number/range; text-like inputs and the
    # default-type path keep the existing string-payload InputComponent behavior.
    for input_type in ("text", "email", "password", "file"):
        comp = InputComponent.create(type=input_type, on_change=_InputTestState.set_v)

        assert isinstance(comp, InputComponent), input_type
        arg = _on_change_arg(comp)
        assert type(arg).__name__ == "StringCastedVar", input_type
        assert arg._var_type is str, input_type

    default_comp = InputComponent.create(on_change=_InputTestState.set_v)
    assert isinstance(default_comp, InputComponent)
    assert type(_on_change_arg(default_comp)).__name__ == "StringCastedVar"


def test_typed_inputs_forward_data_slot_and_default_class(monkeypatch) -> None:
    # The dispatch must not drop buridan-ui styling: data_slot and the default
    # class_name are applied before delegating to the typed component.
    for input_type, typed_cls in (
        ("checkbox", CheckboxInput),
        ("number", ValueNumberInput),
        ("range", ValueNumberInput),
    ):
        captured = _capture_typed_create_props(monkeypatch, typed_cls)

        InputComponent.create(type=input_type)

        assert captured["type"] == input_type
        assert captured["data_slot"] == "input"
        assert ClassNames.INPUT in str(captured["class_name"]), input_type


def test_typed_inputs_do_not_forward_unstyled(monkeypatch) -> None:
    """Guard the wrapper's `props.pop("unstyled", None)` before delegation.

    Simulates the `render_` early-return path of `set_class_name`, where
    `unstyled` is left in props. The dispatched typed components are not
    `CoreComponent`s, so they would otherwise siphon `unstyled` into the
    rendered `css` style dict; the wrapper must strip it itself.
    """
    monkeypatch.setattr(
        InputComponent,
        "set_class_name",
        classmethod(lambda cls, default_class_name, props: None),
    )

    for input_type, typed_cls in (
        ("checkbox", CheckboxInput),
        ("number", ValueNumberInput),
        ("range", ValueNumberInput),
    ):
        captured = _capture_typed_create_props(monkeypatch, typed_cls)

        InputComponent.create(type=input_type, unstyled=True, class_name="custom-input")

        assert "unstyled" not in captured, (input_type, captured)


def test_typed_inputs_unstyled_does_not_leak_onto_dom() -> None:
    from components.ui.input import input

    for input_type in ("checkbox", "number", "range"):
        comp = input(type=input_type, unstyled=True, class_name="custom-input")

        rendered = json.dumps(comp.render())

        assert isinstance(comp, (CheckboxInput, ValueNumberInput))
        assert "unstyled" not in rendered, input_type


def test_typed_dispatch_matches_upstream_contract() -> None:
    """The wrapper must produce the same typed classes and on_change arg types
    as the upstream BaseInput.create dispatch it wraps."""
    for input_type, expected_cls in (
        ("checkbox", CheckboxInput),
        ("number", ValueNumberInput),
        ("range", ValueNumberInput),
    ):
        on_change = cast(Any, _InputTestState.set_v)
        wrapper_comp = InputComponent.create(type=input_type, on_change=on_change)
        upstream_comp = BaseInput.create(
            type=cast(Any, input_type), on_change=on_change
        )

        assert isinstance(upstream_comp, expected_cls), input_type
        assert type(wrapper_comp) is type(upstream_comp), input_type
        assert type(_on_change_arg(wrapper_comp)) is type(
            _on_change_arg(upstream_comp)
        ), input_type
