# pyright: reportUnknownMemberType=false
"""Tests for field components."""

import sys
from pathlib import Path
from typing import Any, cast

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.field import field  # noqa: E402


def test_field_separator_with_children_creates_content_span() -> None:
    separator = field.separator("Or continue with")

    assert cast("Any", separator).custom_attrs["data-content"] == "true"
    assert len(separator.children) == 2

    content = separator.children[1]
    assert type(content).__name__ == "Span"
    assert cast("Any", content).custom_attrs["data-slot"] == "field-separator-content"
    assert "Or continue with" in str(content.render())


def test_field_separator_without_children_keeps_only_divider() -> None:
    separator = field.separator()

    assert cast("Any", separator).custom_attrs["data-content"] == "false"
    assert len(separator.children) == 1
    assert type(separator.children[0]).__name__ != "Span"


def test_field_description_balances_text_on_matching_orientation_value() -> None:
    description = field.description("A helper description")

    class_name = cast("Any", description).class_name
    assert "group-data-[orientation=horizontal]/field:text-balance" in class_name
    assert "group-has-data-horizontal/field:text-balance" not in class_name


def test_field_root_horizontal_orientation_matches_description_selector() -> None:
    root = field.root(orientation="horizontal")

    assert cast("Any", root).custom_attrs["data-orientation"] == "horizontal"
