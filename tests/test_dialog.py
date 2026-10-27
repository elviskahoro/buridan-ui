"""Regression tests for the Dialog wrapper around the pinned ``@base-ui/react``
dependency (``1.6.0``; see ``components/ui/core.py``).

Bug: ``DialogRoot`` declared ``dismissible: Var[bool]``, a prop the pinned
``Dialog.Root`` no longer accepts -- upstream renamed it to
``disablePointerDismissal``. Because ``Dialog.Root`` is a React component (not a
DOM element), React silently dropped the unknown prop, so
``dialog.root(dismissible=False, ...)`` left the dialog fully dismissible with
no warning. The fix removes the dead prop and exposes
``disable_pointer_dismissal: Var[bool]`` instead.

These tests guard against the footgun recurring: (a) the dead prop is gone from
the public API, (b) the 1.6.0-supported replacement is declared, and (c) it
forwards as the camelCase prop ``Dialog.Root`` consumes.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.core import BaseUIComponent
from components.ui.dialog import DialogRoot


def _rendered(component: BaseUIComponent) -> str:
    return " ".join(component.render()["props"])


def test_dialog_root_does_not_declare_dismissible() -> None:
    """The dead prop must be removed from the wrapper's public API surface."""
    assert "dismissible" not in DialogRoot.get_props()


def test_dialog_root_declares_disable_pointer_dismissal() -> None:
    """The 1.6.0-supported replacement must be present as a typed Var prop."""
    assert "disable_pointer_dismissal" in DialogRoot.get_props()


def test_disable_pointer_dismissal_forwards_as_camel_case_top_level_prop() -> None:
    """The declared prop forwards as a top-level ``disablePointerDismissal``
    React prop -- the form ``Dialog.Root`` 1.6.0 consumes -- and NOT into the
    ``css`` style dict (where reflex routes undeclared kwargs). Both ``True``
    and ``False`` must serialize distinctly so an explicit value round-trips.
    """
    assert "disablePointerDismissal:true" in _rendered(
        DialogRoot.create(disable_pointer_dismissal=True),
    )
    assert "disablePointerDismissal:false" in _rendered(
        DialogRoot.create(disable_pointer_dismissal=False),
    )
    assert "css:" not in _rendered(DialogRoot.create(disable_pointer_dismissal=True))
