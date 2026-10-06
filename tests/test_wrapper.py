"""Regression guards for the demo preview container in ``demo_wrapper``.

The preview ``class_name`` must use 8px padding on small screens and override
it with 24px from the ``sm`` breakpoint up. v0.9.1 (commit 755f3ed) lowered the
mobile base to ``!p-2`` and restored 24px at ``sm`` via ``!sm:p-6`` — but the
important marker placed *before* the ``sm:`` variant makes ``!sm:p-6`` invalid
Tailwind v3/v4 syntax: the compiler silently emits no rule for it, so the
``!p-2`` (8px, ``!important``) base wins at every viewport and the ``sm``
override never applies. These tests pin the corrected ``sm:!p-6`` ordering and
guard against the malformed ``!<variant>:`` pattern recurring anywhere in the
wrapper module.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import cast

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx
from reflex.components.component import Component

from app.www import wrapper

WRAPPER_PATH = Path(wrapper.__file__)
EXPECTED_PREVIEW_CLASS_NAME = (
    "w-full min-h-[250px] flex items-center justify-center !p-2 sm:!p-6 my-10"
)

# A malformed Tailwind important+variant token: '!' placed *before* the
# variant prefix (e.g. ``!sm:p-6``). Neither v3 nor v4 emits a rule for it.
# Anchored to a class-token boundary (quote or whitespace) so bare ``!p-2``
# (no colon) and valid ``sm:!p-6`` / ``md:!hidden`` (variant first, '!' after
# the colon with no trailing colon) are never matched.
_MALFORMED_IMPORTANT_VARIANT = re.compile(r"(?:[\s\"']![a-z][a-z0-9-]*:)")


def _preview_div(demo: Component) -> Component:
    """Return the live-preview inner div (first child of demo_wrapper)."""
    children = demo.children
    assert len(children) == 2, "demo_wrapper should render preview + code panel"
    preview = cast(Component, children[0])
    assert type(preview).__name__ == "Div"
    assert getattr(preview, "tag", None) == "div"
    return preview


def test_demo_wrapper_preview_class_name_is_exactly_the_fixed_value() -> None:
    """Pin the full preview ``class_name`` to catch any drift in the demo box.

    Asserting the exact string also confirms the ``sm``-breakpoint override uses
    the valid ``sm:!p-6`` ordering (variant first, then ``!``) and that the
    malformed ``!sm:p-6`` token is absent -- ``!sm:p-6`` is dropped by Tailwind,
    leaving ``!p-2`` (8px) to win at every viewport.
    """
    demo = wrapper.demo_wrapper(rx.el.div("hello"), source='print("hi")')
    assert str(_preview_div(demo).class_name) == EXPECTED_PREVIEW_CLASS_NAME


def test_wrapper_module_has_no_malformed_important_variant_tokens() -> None:
    """Scan ``app/www/wrapper.py`` for the malformed ``!<variant>:`` shape.

    Tailwind silently ignores ``!<variant>:`` tokens (e.g. ``!sm:p-6``) -- no
    CSS is emitted. Valid forms are ``!p-2`` (bare important, no colon) and
    ``sm:!p-6`` / ``md:!hidden`` (variant first, important after the colon) --
    neither matches the anchored regex.
    """
    source = WRAPPER_PATH.read_text(encoding="utf-8")
    offenders = _MALFORMED_IMPORTANT_VARIANT.findall(source)
    assert offenders == [], (
        f"malformed Tailwind `!<variant>:` token(s) found in wrapper.py: {offenders}"
    )
