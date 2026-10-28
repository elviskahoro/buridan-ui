"""Regression tests for the Tabs wrapper around the pinned ``@base-ui/react``
dependency (``1.6.0``; see ``components/ui/core.py``).

``TabsList.loop`` was a dead prop: the pinned ``Tabs.List`` consumes
``loopFocus`` (not ``loop``), so React silently dropped the unknown prop. The
audit renames ``loop`` -> ``loop_focus`` to match the 1.6.0 ``loopFocus`` prop.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.tabs import TabsList  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_tabs_list_no_longer_declares_dead_loop() -> None:
    props = TabsList.get_props()
    assert "loop" not in props
    assert "loop_focus" in props


def test_tabs_list_loop_focus_forwards_as_camel_case_top_level_prop() -> None:
    """``loop_focus`` forwards as the top-level ``loopFocus`` React prop that
    ``Tabs.List`` 1.6.0 consumes, and NOT into the ``css`` style dict.
    """
    assert "loopFocus:true" in _rendered(TabsList.create(loop_focus=True))
    assert "loopFocus:false" in _rendered(TabsList.create(loop_focus=False))
    assert "css:" not in _rendered(TabsList.create(loop_focus=True))
