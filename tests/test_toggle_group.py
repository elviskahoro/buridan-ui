"""Regression tests for the ToggleGroup wrapper around the pinned
``@base-ui/react`` dependency (``1.6.0``; see ``components/ui/core.py``).

``ToggleGroupRoot.loop`` was a dead prop: the pinned ``ToggleGroup`` consumes
``loopFocus`` (not ``loop``), so React silently dropped the unknown prop. The
audit renames ``loop`` -> ``loop_focus`` to match the 1.6.0 ``loopFocus`` prop.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.toggle_group import ToggleGroupRoot  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_toggle_group_root_no_longer_declares_dead_loop() -> None:
    props = ToggleGroupRoot.get_props()
    assert "loop" not in props
    assert "loop_focus" in props


def test_toggle_group_root_loop_focus_forwards_as_camel_case_top_level_prop() -> None:
    """``loop_focus`` forwards as the top-level ``loopFocus`` React prop that
    ``ToggleGroup`` 1.6.0 consumes.

    ``ToggleGroupRoot`` legitimately injects a ``css`` gap style, so the
    camelCase top-level forwarding -- not the absence of any ``css`` -- is what
    confirms the prop is declared rather than dropped into the inert ``css``
    style dict.
    """
    assert "loopFocus:true" in _rendered(ToggleGroupRoot.create(loop_focus=True))
    assert "loopFocus:false" in _rendered(ToggleGroupRoot.create(loop_focus=False))
