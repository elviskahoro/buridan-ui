"""Tests for the field getting-started demo."""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.examples.field_general import field_demo  # noqa: E402
from tests.render_helpers import render_text


def test_expiry_month_and_year_selects_default_to_placeholder_value() -> None:
    rendered = render_text(field_demo())

    default_values = re.findall(r"defaultValue:\"([^\"]*)\"", rendered)

    assert len(default_values) == 2
    assert default_values == ["", ""]
