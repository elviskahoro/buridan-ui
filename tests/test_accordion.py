# noqa: INP001
"""Regression guards for the Accordion double-header bug.

Since v0.9.1 (commit ``755f3ed``) ``AccordionTrigger.create`` in
``components/ui/accordion.py`` auto-wraps its trigger in an ``AccordionHeader``
(Base UI renders ``Accordion.Header`` as an ``<h3>``). Any call site that *also*
wraps the trigger in an explicit ``accordion.header(...)`` therefore produces
``Accordion.Header > Accordion.Header > Accordion.Trigger`` -- i.e. an ``<h3>``
nested inside an ``<h3>``, which is invalid HTML and a duplicated heading in the
accessibility tree.

The fix removed the explicit ``accordion.header(...)`` wrapper from
``app/anatomy_src/accordion.py`` and ``app/examples/components.py`` and added a
defensive guard in ``AccordionHeader.create`` that rejects the double-wrap
loudly so the mismatch can't silently recur. These tests pin the auto-wrap
contract, the guard, and guard against the stale pattern being re-introduced by
hand.
"""

import re
from pathlib import Path
from typing import cast

import pytest
import reflex as rx
from reflex.components.component import Component

from components.ui.accordion import (
    AccordionHeader,
    AccordionItem,
    AccordionTrigger,
    accordion,
)

ROOT_DIR = Path(__file__).parent.parent

# ``Accordion.Header`` rendered tag, the element Base UI promotes to ``<h3>``.
_HEADER_TAG = "Accordion.Header"
# Regex-escaped form for ``pytest.raises(match=...)`` -- RUF043 requires that a
# pattern containing regex metacharacters (``.``) be escaped or raw.
_HEADER_TAG_RE = re.escape(_HEADER_TAG)


# ---------------------------------------------------------------------------
# Tree-walking helpers (operate on the reflex component tree in-process)
# ---------------------------------------------------------------------------


def _children(node: Component) -> list[Component]:
    """Return ``node.children`` typed as a list of components."""
    return cast("list[Component]", getattr(node, "children", []))


def _direct_child_names(comp: Component) -> list[str]:
    """Return the ``tag`` (Base UI) or class name of each direct child."""
    names: list[str] = []
    for child in _children(comp):
        tag = getattr(child, "tag", None)
        names.append(tag if tag is not None else type(child).__name__)
    return names


def _find_first(root: Component, cls: type) -> Component:
    """Breadth-first search for the first descendant of ``cls``."""
    queue: list[Component] = list(_children(root))
    while queue:
        node = queue.pop(0)
        if isinstance(node, cls):
            return node
        queue.extend(_children(node))
    msg = f"No {cls.__name__} found under {type(root).__name__}"
    raise AssertionError(msg)  # noqa: TRY003


def _count_nested_headers(comp: Component) -> int:
    """Count ``AccordionHeader`` nodes that are themselves descendants of
    another ``AccordionHeader`` -- the structural signature of the bug.
    """
    nested = 0
    frontier: list[tuple[Component, bool]] = [(comp, False)]
    while frontier:
        node, inside_header = frontier.pop()
        is_header = isinstance(node, AccordionHeader)
        if is_header and inside_header:
            nested += 1
        for child in _children(node):
            frontier.append((child, inside_header or is_header))
    return nested


# ---------------------------------------------------------------------------
# 1. AccordionTrigger auto-wrap contract (the reason the double-wrap is a bug)
# ---------------------------------------------------------------------------


def test_trigger_self_wraps_in_exactly_one_header() -> None:
    """``accordion.trigger(...)`` must return an ``AccordionHeader`` whose sole
    accordion child is an ``AccordionTrigger`` -- the auto-wrap from v0.9.1.
    This is the contract that makes an explicit ``accordion.header(...)`` around
    a trigger a double-wrap.
    """
    trigger = accordion.trigger("Section title")
    assert isinstance(trigger, AccordionHeader)
    assert len(trigger.children) == 1
    assert isinstance(trigger.children[0], AccordionTrigger)
    # No nested header inside the auto-wrapped header.
    assert _count_nested_headers(trigger) == 0


def test_item_with_bare_trigger_has_exactly_one_header_not_nested() -> None:
    """The post-v0.9.1 correct composition: trigger placed directly under item.
    The item must contain exactly one ``AccordionHeader`` (the auto-wrap), and
    that header must contain a single ``AccordionTrigger`` -- never a nested
    header.
    """
    item = accordion.item(
        accordion.trigger("Question?"),
        accordion.panel("Answer."),
        value="item-1",
    )
    assert isinstance(item, AccordionItem)

    direct = _direct_child_names(item)
    assert direct.count(_HEADER_TAG) == 1
    assert "Accordion.Panel" in direct

    header = _find_first(item, AccordionHeader)
    assert len(header.children) == 1
    assert isinstance(header.children[0], AccordionTrigger)
    assert _count_nested_headers(item) == 0


def test_trigger_render_escape_hatch_still_self_wraps() -> None:
    """``render_`` replaces the trigger's own element but the auto-wrap header
    must still be produced (otherwise the trigger would render without a
    heading wrapper). The double-wrap guard must not interfere.
    """
    trigger = accordion.trigger(render_=rx.el.button("toggle"))
    assert isinstance(trigger, AccordionHeader)
    assert isinstance(trigger.children[0], AccordionTrigger)
    assert _count_nested_headers(trigger) == 0


# ---------------------------------------------------------------------------
# 2. Defensive guard in AccordionHeader.create
# ---------------------------------------------------------------------------


def test_header_rejects_wrapping_an_already_wrapped_trigger() -> None:
    """The bug pattern: ``accordion.header(accordion.trigger(...))``. The
    trigger already self-wraps in a Header, so this nests ``Accordion.Header``
    inside ``Accordion.Header``. ``AccordionHeader.create`` must reject it
    loudly instead of silently shipping invalid ``<h3>`` nesting.
    """
    with pytest.raises(TypeError, match=_HEADER_TAG_RE):
        accordion.header(accordion.trigger("Q?"))


def test_header_rejects_wrapping_an_explicit_header() -> None:
    """The guard is structural (rejects any ``AccordionHeader`` child), so it
    also catches the general ``accordion.header(accordion.header(...))`` shape
    -- not just the trigger-derived form.
    """
    inner = AccordionHeader.create(rx.el.div("X"))
    with pytest.raises(TypeError, match=_HEADER_TAG_RE):
        AccordionHeader.create(inner)


def test_header_accepts_non_header_children() -> None:
    """The guard must not over-fire: a header wrapping a plain element or a
    string is legitimate (e.g. an explicit heading that does not involve a
    trigger). The guard only rejects ``AccordionHeader`` children, not plain
    elements/text.
    """
    header_with_div = accordion.header(rx.el.div("just a heading"))
    assert isinstance(header_with_div, AccordionHeader)
    assert _count_nested_headers(header_with_div) == 0

    header_with_text = AccordionHeader.create("plain heading text")
    assert isinstance(header_with_text, AccordionHeader)
    assert _count_nested_headers(header_with_text) == 0


def test_header_guard_does_not_break_internal_trigger_autowrap() -> None:
    """``AccordionTrigger.create`` internally calls
    ``AccordionHeader.create(trigger)`` with an ``AccordionTrigger`` (not a
    Header). The guard must allow this internal call so the auto-wrap still
    works.
    """
    trigger = AccordionTrigger.create("X")
    assert isinstance(trigger, AccordionHeader)
    assert isinstance(trigger.children[0], AccordionTrigger)


# ---------------------------------------------------------------------------
# 3. Source-level guards against the stale pattern being re-introduced by hand
# ---------------------------------------------------------------------------


def test_anatomy_source_file_has_no_explicit_header_wrap_around_trigger() -> None:
    """The authored ``app/anatomy_src/accordion.py`` must not contain the
    pre-v0.9.1 double-wrap pattern ``accordion.header(accordion.trigger(...))``.
    Guards against the stale pattern being re-introduced by hand.
    """
    source = (ROOT_DIR / "app" / "anatomy_src" / "accordion.py").read_text(
        encoding="utf-8",
    )
    assert "accordion.header(" not in source, (
        "app/anatomy_src/accordion.py still wraps a trigger in accordion.header(...) "
        "-- this double-wraps the trigger (which auto-wraps in a Header) and produces "
        "nested <h3> elements. Use accordion.trigger() directly under accordion.item()."
    )


def test_examples_components_source_has_no_explicit_header_wrap_around_trigger() -> (
    None
):
    """``app/examples/components.py`` must not contain the double-wrap pattern
    ``accordion.header(accordion.trigger(...))``. Guards against the stale
    pattern being re-introduced in the live docs-site examples.
    """
    source = (ROOT_DIR / "app" / "examples" / "components.py").read_text(
        encoding="utf-8",
    )
    # The trigger already self-wraps in a Header, so any explicit
    # ``accordion.header(...)`` call in this file would double-wrap. The trigger
    # should be placed directly under the item instead.
    assert "accordion.header(" not in source, (
        "app/examples/components.py still wraps a trigger in accordion.header(...) "
        "-- this double-wraps the trigger (which auto-wraps in a Header) and produces "
        "nested <h3> elements on the live docs site."
    )
