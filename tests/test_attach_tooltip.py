"""Regression tests for the ``attach_tooltip`` helper in ``app/templates/utils.py``.

``attach_tooltip`` is the shared helper that attaches a tooltip to the navbar and
searchbar chrome controls (theme toggle, GitHub button, search button). It must
forward the caller's already-interactive component to ``Tooltip.Trigger`` via the
``render_`` prop rather than as a positional child.

Passing the caller's component as a positional child caused Base UI's
``Tooltip.Trigger`` (which renders a default ``<button>`` when no ``render``/``
render_`` is supplied) to wrap the caller's real ``<button>`` in another ``<button>``,
producing invalid nested-interactive HTML on every page (duplicate tab stops,
double focus rings, and duplicated button semantics for screen-reader users).
"""

from collections.abc import Iterable

import pytest
import reflex as rx

from app.templates.navbar import light_and_dark_toggle, site_github
from app.templates.searchbar import searchbar
from app.templates.utils import attach_tooltip
from components.ui.button import button
from components.ui.tooltip import (
    ClassNames,
    TooltipTrigger,
)


def _walk(component: rx.Component) -> Iterable[rx.Component]:
    yield component
    for child in getattr(component, "children", None) or []:
        yield from _walk(child)


def _find_all(component: rx.Component, cls: type) -> list[rx.Component]:
    return [node for node in _walk(component) if isinstance(node, cls)]


def test_attach_tooltip_passes_caller_via_render_prop() -> None:
    """The caller's component must be forwarded via ``render_``, never as a positional
    child, so Base UI's ``Tooltip.Trigger`` adopts the caller's button as its trigger
    instead of rendering its own default ``<button>`` wrapper.

    Regression for the form ``tooltip.trigger(func)`` which produced
    ``TooltipTrigger(render_=None, children=[Button])`` and rendered
    ``<button data-slot="tooltip-trigger"><button data-slot="button">…</button></button>``.
    """
    result = attach_tooltip(button("Toggle", variant="ghost"), "Toggle Theme")

    triggers = _find_all(result, TooltipTrigger)
    assert len(triggers) == 1
    trigger = triggers[0]

    # No positional children: the caller's button is not nested inside the trigger.
    assert trigger.children == []
    # The render prop is set, so Base UI clones the caller's button instead of
    # falling back to its own default `<button>`.
    rendered_props = " ".join(trigger.render()["props"])
    assert "render:" in rendered_props
    # The trigger's default centering classes are merged onto the caller's button, so
    # switching to `render_=` does not drop the layout the old wrapper provided.
    assert ClassNames.TRIGGER in rendered_props


@pytest.mark.parametrize(
    "factory",
    [light_and_dark_toggle, site_github, searchbar],
    ids=["light_and_dark_toggle", "site_github", "searchbar"],
)
def test_navbar_and_searchbar_tooltip_triggers_use_render_prop(factory: object) -> None:
    """Each chrome control that goes through ``attach_tooltip`` must produce a
    ``Tooltip.Trigger`` with the caller's button as its ``render_`` target and zero
    positional children. Guards against refactoring a call site to bypass the helper.
    """
    comp = factory()  # type: ignore[operator]

    triggers = _find_all(comp, TooltipTrigger)
    assert triggers, "expected at least one Tooltip.Trigger in this chrome control"

    for trigger in triggers:
        assert trigger.children == [], (
            "Tooltip.Trigger must not have positional children; the caller's button "
            "must be passed via render_"
        )
        rendered_props = " ".join(trigger.render()["props"])
        assert "render:" in rendered_props
        assert ClassNames.TRIGGER in rendered_props
