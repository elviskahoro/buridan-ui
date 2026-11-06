# pyright: reportUnknownMemberType=false
"""Tests for the field getting-started demo."""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.examples.field_general import field_demo  # noqa: E402


def test_expiry_month_and_year_selects_default_to_placeholder_value() -> None:
    rendered = str(field_demo().render())

    default_values = re.findall(r"defaultValue:\"([^\"]*)\"", rendered)

    assert len(default_values) == 2
    assert default_values == ["", ""]
