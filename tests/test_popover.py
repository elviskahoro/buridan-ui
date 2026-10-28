"""Regression tests for the Popover wrapper's audit of dead Base UI 1.6.0 props.

``PopoverRoot`` previously declared ``open_on_hover``, ``delay`` and
``close_delay`` -- props the pinned ``@base-ui/react@1.6.0`` moved from
``Popover.Root`` onto ``Popover.Trigger``. Declared on Root, React silently
dropped them (the same dead-prop pattern as ``DialogRoot.dismissible``). The
audit removes them from Root and re-exposes them on ``PopoverTrigger``, where
1.6.0 actually consumes them.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent  # noqa: E402
from components.ui.popover import PopoverRoot, PopoverTrigger  # noqa: E402


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_popover_root_no_longer_declares_dead_hover_props() -> None:
    """The relocated props must be removed from the Root's public API."""
    props = PopoverRoot.get_props()
    assert "open_on_hover" not in props
    assert "delay" not in props
    assert "close_delay" not in props


def test_popover_trigger_hover_props_forward_as_camel_case() -> None:
    """The relocated props are re-exposed on the component 1.6.0 consumes them
    on (``Popover.Trigger``) and forward as the camelCase top-level props
    ``openOnHover``/``delay``/``closeDelay``. Asserting the forwarded form also
    confirms they are declared on the Trigger (an undeclared kwarg would route to
    the inert ``css`` style dict instead).
    """
    rendered = _rendered(
        PopoverTrigger.create(open_on_hover=True, delay=300, close_delay=100),
    )
    assert "openOnHover:true" in rendered
    assert "delay:300" in rendered
    assert "closeDelay:100" in rendered
