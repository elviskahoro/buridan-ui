"""Regression tests for the Toggle wrapper's ``icon_variant`` styling prop.

``Toggle.icon_variant`` is a wrapper-only styling prop: it selects a pressed-icon
class (``ICON_VARIANT_CLASSES``) and must NOT be forwarded to ``Toggle`` as a
React prop, because the pinned ``ToggleProps`` (1.6.0) declares no
``iconVariant``. Previously ``icon_variant`` was neither popped in ``create()``
nor listed in ``_exclude_props()``, so it leaked through as a dead
``iconVariant`` React prop. The audit adds it to ``_exclude_props`` (mirroring
``variant``/``size``) while keeping it declared and applied for styling.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.toggle import ClassNames, Toggle  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_toggle_icon_variant_still_declared_and_applied_for_styling() -> None:
    """``icon_variant`` remains a typed prop and still selects the pressed-icon
    class so existing callers (e.g. ``toggle(icon_variant="fill")``) keep working.
    """
    assert "icon_variant" in Toggle.get_props()

    pressed = " ".join(str(c) for c in [Toggle.create(icon_variant="fill").class_name])
    assert ClassNames.ICON_VARIANT_CLASSES["fill"] in pressed


def test_toggle_icon_variant_not_forwarded_as_react_prop() -> None:
    """``icon_variant`` is wrapper-only: it must not leak through to ``Toggle`` as
    a dead ``iconVariant`` React prop (``ToggleProps`` 1.6.0 declares no
    ``iconVariant``).
    """
    assert "iconVariant" not in _rendered(Toggle.create(icon_variant="fill"))
