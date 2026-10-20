"""Regression guards for docs-navigation visibility across viewport widths.

On documentation pages the docs sidebar (``sidebar()``) is the primary browse
affordance for the doc tree, and the navbar's ``mobile_menu()`` is its
small-screen counterpart. The two must use complementary Tailwind responsive
classes so that at every viewport width at least one of them is visible —
there is no third affordance for browsing the docs structure.

Commit ``6500d1e`` ("add mobile navigation") introduced ``mobile_menu()`` with
a ``flex md:hidden`` wrapper while the sidebar stayed at ``hidden lg:flex``.
Tailwind's ``md`` (768px) and ``lg`` (1024px) breakpoints are distinct, so the
768–1023px tablet band showed *neither* affordance. These tests pin the
invariant that the two affordances never leave a viewport width with no docs
navigation, and that their responsive cutoffs stay in sync.
"""

import re
import sys
from pathlib import Path
from typing import cast

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from reflex.components.component import Component

from app.templates.docsidebar import sidebar
from app.templates.navbar import navbar

# Tailwind default ``min-width`` media-query breakpoints (px).
_TAILWIND_BP_MIN = {"sm": 640, "md": 768, "lg": 1024, "xl": 1280}


def _mobile_menu_wrapper_class() -> str:
    """Return the class_name of the navbar div that wraps ``mobile_menu()``.

    The navbar header's inner container has exactly three children; index 1 is
    the mobile-menu wrapper.
    """
    header = navbar()
    container = cast("Component", header.children[0])
    assert len(container.children) == 3, (
        "navbar layout drifted: expected 3 children in the inner container"
    )
    mobile_wrapper = cast("Component", container.children[1])
    assert type(mobile_wrapper).__name__ == "Div"
    return str(mobile_wrapper.class_name)


def _sidebar_wrapper_class() -> str:
    """Return the class_name of the docs sidebar's outermost wrapper div."""
    return str(cast("Component", sidebar()).class_name)


def _is_displayed_at(width: int, class_name: str) -> bool:
    """Model Tailwind's responsive ``display`` semantics for a class string.

    Tailwind emits the bare utility as the base, then ``<bp>:<util>`` as
    ``@media (min-width: <bp>)`` rules in ascending breakpoint order, so the
    active variant with the *largest* qualifying breakpoint wins. Returns
    ``True`` only if the resolved display is not ``hidden``.
    """
    tokens = class_name.split()
    display = (
        "hidden" if "hidden" in tokens else ("flex" if "flex" in tokens else "block")
    )
    for bp, min_w in sorted(_TAILWIND_BP_MIN.items(), key=lambda kv: kv[1]):
        if width >= min_w:
            if f"{bp}:flex" in tokens:
                display = "flex"
            elif f"{bp}:hidden" in tokens:
                display = "hidden"
    return display != "hidden"


def test_no_dead_zone_between_mobile_menu_and_sidebar() -> None:
    """The two docs-navigation affordances must use the *same* breakpoint.

    The mobile-menu's hide breakpoint (e.g. ``lg:hidden``) must equal the
    sidebar's show breakpoint (e.g. ``hidden lg:flex``) so the two ranges are
    exactly complementary: at every viewport width one transitions as the other
    does, leaving no window where both are hidden (a dead zone). Asserting
    equality — not a specific breakpoint — keeps this valid if the project
    legitimately moves both cutoffs together (e.g. to ``xl`` to match upstream),
    while still catching the ``md``/``lg`` mismatch from ``6500d1e`` recurring
    in either direction.
    """
    mobile_class = _mobile_menu_wrapper_class()
    sidebar_class = _sidebar_wrapper_class()

    mobile_hide_bps = set(re.findall(r"\b(sm|md|lg|xl):hidden\b", mobile_class))
    sidebar_show_bps = set(re.findall(r"\b(sm|md|lg|xl):flex\b", sidebar_class))

    assert mobile_hide_bps == sidebar_show_bps, (
        "mobile-menu hide breakpoints and sidebar show breakpoints must match "
        "to avoid a dead zone; "
        f"mobile-hide={mobile_hide_bps} sidebar-show={sidebar_show_bps}"
    )


def test_docs_navigation_visible_at_every_viewport_width() -> None:
    """At least one docs-navigation affordance is visible at every viewport width.

    Simulates Tailwind's responsive display semantics across the full viewport
    range (320px mobile up to 1920px desktop), with a dense sweep through the
    768–1023px tablet band that the bug left without navigation, and the exact
    ``lg`` boundary (1023px and 1024px). At *every* sampled width at least one
    of the mobile-menu wrapper or the docs sidebar must be displayed.
    """
    mobile_class = _mobile_menu_wrapper_class()
    sidebar_class = _sidebar_wrapper_class()

    widths = sorted(
        {
            *range(320, 768, 40),
            *range(768, 1024, 32),
            1023,  # just below lg
            1024,  # lg and up
            1440,  # desktop
            *range(1024, 1920, 64),
        }
    )

    dead_zone_widths = [
        width
        for width in widths
        if not _is_displayed_at(width, mobile_class)
        and not _is_displayed_at(width, sidebar_class)
    ]

    assert not dead_zone_widths, (
        f"viewport widths with no docs-navigation affordance visible: "
        f"{dead_zone_widths} (mobile class={mobile_class!r}, "
        f"sidebar class={sidebar_class!r})"
    )
