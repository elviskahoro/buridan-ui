import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.input import BaseInput, ClassNames, InputComponent


def _capture_input_props(monkeypatch) -> dict:
    """Capture props passed to the underlying Reflex input component."""
    captured = {}

    def create(cls, *children, **props):
        captured.update(props)
        return props

    monkeypatch.setattr(BaseInput, "create", classmethod(create))
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
