"""Regression tests for the Slider wrapper around the pinned ``@base-ui/react``
dependency (``1.6.0``; see ``components/ui/core.py``).

``SliderRoot.input_ref`` was a dead prop: it forwarded ``inputRef`` to
``Slider.Root``, but the pinned ``SliderRootProps`` declares no ``inputRef``
(the 1.6.0 slider Root has no hidden input, unlike ``SelectRoot``/``SwitchRoot``
which do). Declared on the wrapper, React silently dropped it. The audit removes
it; the slider Root has no hidden-input ref surface.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.slider import SliderRoot  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_slider_root_no_longer_declares_input_ref() -> None:
    """The dead ``input_ref`` prop must be removed from the wrapper's public API
    surface -- ``Slider.Root`` 1.6.0 declares no ``inputRef``.
    """
    assert "input_ref" not in SliderRoot.get_props()


def test_slider_root_does_not_forward_input_ref() -> None:
    """An undeclared ``input_ref`` kwarg routes to the inert ``css`` style dict
    rather than forwarding as a top-level ``inputRef`` React prop.
    """
    assert "inputRef" not in _rendered(SliderRoot.create())
