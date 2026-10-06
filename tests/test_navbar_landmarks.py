"""Regression guard: page templates render a single navbar ``<header>`` landmark.

``navbar()`` returns its own ``rx.el.header(...)`` (the implicit ARIA ``banner``
landmark, with the sticky styling baked in). The page templates must render it
verbatim. An earlier revision wrapped ``navbar()`` in an extra
``rx.el.header(...)``, which produced ``<header><header>...</header></header>``
-- invalid HTML (an ``header`` may not descend from another ``header``) and a
duplicate ``banner`` landmark on every docs and layout page. These tests pin
one ``<header>`` per page so the redundant wrapper cannot silently return.
"""

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx

from app.templates.docpage import docpage
from app.templates.layout import layout_decorator
from app.templates.navbar import navbar


def _walk(component: Any) -> Iterator[Any]:
    """Yield ``component`` and every descendant, depth-first."""
    yield component
    for child in getattr(component, "children", []) or []:
        yield from _walk(child)


def _count_tag(root: Any, tag: str) -> int:
    """Count component nodes whose ``tag`` attribute equals ``tag``."""
    return sum(1 for node in _walk(root) if getattr(node, "tag", None) == tag)


def test_navbar_returns_a_single_header_landmark() -> None:
    """``navbar()`` is itself the single banner landmark -- it must not wrap a
    ``<header>`` (the root cause of the duplicate-banner bug) nor return a
    non-``<header>``, both of which would change the page-template contract."""
    assert _count_tag(navbar(), "header") == 1


def test_docpage_renders_a_single_header() -> None:
    """``docpage`` must render ``navbar()`` directly, not re-wrapped in a
    ``<header>`` (one banner per docs page; a single header cannot be nested)."""
    page = docpage(rx.el.div("content"), rx.el.div("toc"))
    assert _count_tag(page, "header") == 1


def test_layout_decorator_renders_a_single_header() -> None:
    """``layout_decorator`` must render ``navbar()`` directly, not re-wrapped in
    a ``<header>`` (one banner per landing/components/charts/blocks page)."""
    decorator = layout_decorator("Title", "Description", ctas=[])

    @decorator
    def page() -> Any:
        return rx.el.div("content")

    assert _count_tag(page(), "header") == 1
