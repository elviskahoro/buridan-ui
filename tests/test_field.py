"""Tests for field components."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.field import field  # noqa: E402


def test_field_separator_with_children_creates_content_span() -> None:
    separator = field.separator("Or continue with")

    assert separator.custom_attrs["data-content"] == "true"
    assert len(separator.children) == 2

    content = separator.children[1]
    assert type(content).__name__ == "Span"
    assert content.custom_attrs["data-slot"] == "field-separator-content"
    assert "Or continue with" in str(content.render())


def test_field_separator_without_children_keeps_only_divider() -> None:
    separator = field.separator()

    assert separator.custom_attrs["data-content"] == "false"
    assert len(separator.children) == 1
    assert type(separator.children[0]).__name__ != "Span"
