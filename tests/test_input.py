import json
import sys
from pathlib import Path
from typing import Any, cast

import pytest
import reflex as rx
from reflex.event import EventChain, EventSpec
from reflex.vars.base import Var
from reflex_components_core.el.elements.forms import CheckboxInput, ValueNumberInput

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.input import (
    BaseInput,
    ClassNames,
    InputComponent,
)


class _InputTestState(rx.State):  # pyright: ignore[reportUntypedBaseClass]
    v: int = 0
    b: bool = False

    def set_v(self, v: Any) -> None:  # noqa: ANN401
        self.v = v

    def set_b(self, b: Any) -> None:  # noqa: ANN401
        self.b = b


def _capture_input_props(monkeypatch) -> dict:
    """Capture props passed to the underlying Reflex input component."""
    captured = {}

    def create(cls, *children, **props):
        captured.update(props)
        return props

    monkeypatch.setattr(BaseInput, "create", classmethod(create))
    return captured


def _on_change_arg(comp: rx.Component) -> Var[Any]:  # noqa: ANN401
    chain = comp.event_triggers["on_change"]
    assert isinstance(chain, EventChain)
    spec = chain.events[0]
    assert isinstance(spec, EventSpec)
    return spec.args[0][1]


def _capture_typed_create_props(
    monkeypatch: pytest.MonkeyPatch,
    typed_cls: type,
) -> dict[str, object]:
    captured: dict[str, object] = {}

    def create(_cls: type, *_children: object, **props: object) -> dict[str, object]:
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
    assert arg._var_type is bool  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


def test_number_input_dispatches_with_number_payload() -> None:
    comp = InputComponent.create(type="number", on_change=_InputTestState.set_v)

    assert isinstance(comp, ValueNumberInput)

    arg = _on_change_arg(comp)
    assert type(arg).__name__ == "NumberCastedVar"
    assert arg._var_type is float  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


def test_range_input_dispatches_with_number_payload() -> None:
    comp = InputComponent.create(type="range", on_change=_InputTestState.set_v)

    assert isinstance(comp, ValueNumberInput)

    arg = _on_change_arg(comp)
    assert type(arg).__name__ == "NumberCastedVar"
    assert arg._var_type is float  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


def test_non_typed_inputs_stay_input_component_with_string_payload() -> None:
    # The fix must only reroute checkbox/number/range; text-like inputs and the
    # default-type path keep the existing string-payload InputComponent behavior.
    for input_type in ("text", "email", "password", "file"):
        comp = InputComponent.create(type=input_type, on_change=_InputTestState.set_v)

        assert isinstance(comp, InputComponent), input_type
        arg = _on_change_arg(comp)
        assert type(arg).__name__ == "StringCastedVar", input_type
        assert arg._var_type is str, input_type  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    default_comp = InputComponent.create(on_change=_InputTestState.set_v)
    assert isinstance(default_comp, InputComponent)
    assert type(_on_change_arg(default_comp)).__name__ == "StringCastedVar"


def test_typed_inputs_forward_data_slot_and_default_class(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_typed_inputs_do_not_forward_unstyled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Guard the wrapper's `props.pop("unstyled", None)` before delegation.

    Simulates the `render_` early-return path of `set_class_name`, where
    `unstyled` is left in props. The dispatched typed components are not
    `CoreComponent`s, so they would otherwise siphon `unstyled` into the
    rendered `css` style dict; the wrapper must strip it itself.
    """

    def _noop_set_class_name(
        _cls: type,
        _default_class_name: str,
        _props: dict[str, object],
    ) -> None:
        pass

    monkeypatch.setattr(
        InputComponent,
        "set_class_name",
        classmethod(_noop_set_class_name),
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
    for input_type in ("checkbox", "number", "range"):
        comp = InputComponent.create(
            type=input_type,
            unstyled=True,
            class_name="custom-input",
        )

        rendered = json.dumps(comp.render())

        assert isinstance(comp, (CheckboxInput, ValueNumberInput))
        assert "unstyled" not in rendered, input_type


def test_typed_dispatch_matches_upstream_contract() -> None:
    """The wrapper must produce the same typed classes and on_change arg types
    as the upstream BaseInput.create dispatch it wraps.
    """
    for input_type, expected_cls in (
        ("checkbox", CheckboxInput),
        ("number", ValueNumberInput),
        ("range", ValueNumberInput),
    ):
        on_change = cast("Any", _InputTestState.set_v)
        wrapper_comp = InputComponent.create(type=input_type, on_change=on_change)
        upstream_comp = BaseInput.create(
            type=cast("Any", input_type),
            on_change=on_change,
        )

        assert isinstance(upstream_comp, expected_cls), input_type
        assert type(wrapper_comp) is type(upstream_comp), input_type
        assert type(_on_change_arg(wrapper_comp)) is type(
            _on_change_arg(upstream_comp),
        ), input_type


def test_typed_dispatch_normalizes_value_like_upstream() -> None:
    """Controlled checkbox/number/range inputs bound to a state var must
    render the same null-guarded `value` as upstream BaseInput.create, so
    React does not flap between controlled and uncontrolled.
    """
    for input_type in ("checkbox", "number", "range"):
        wrapper_comp = InputComponent.create(type=input_type, value=_InputTestState.v)
        upstream_comp = BaseInput.create(
            type=cast("Any", input_type),
            value=_InputTestState.v,
        )

        assert type(wrapper_comp) is type(upstream_comp), input_type

        def _value_prop(comp: rx.Component, *, input_type: str) -> str:
            for prop in comp.render()["props"]:
                if prop.startswith("value:"):
                    return prop
            msg = f"no value prop on {input_type}"
            raise AssertionError(msg)

        assert _value_prop(wrapper_comp, input_type=input_type) == _value_prop(
            upstream_comp,
            input_type=input_type,
        ), input_type
