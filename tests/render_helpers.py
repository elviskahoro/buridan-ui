"""Typed wrappers around Reflex's bare-``dict`` ``Component.render()``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from reflex.components.component import BaseComponent, Component


def render_dict(component: BaseComponent) -> dict[str, Any]:
    """Return ``component.render()`` typed as ``dict[str, Any]``."""
    return cast("dict[str, Any]", cast("Any", component).render())


def render_props(component: BaseComponent) -> list[str]:
    """Return the rendered ``props`` list of ``component`` as strings."""
    return [str(p) for p in cast("list[Any]", render_dict(component)["props"])]


def render_text(component: BaseComponent) -> str:
    """Return ``str(component.render())``."""
    return str(render_dict(component))


def custom_attrs(component: BaseComponent) -> dict[str, Any]:
    """Return ``component.custom_attrs`` typed as ``dict[str, Any]``."""
    return cast("dict[str, Any]", cast("Any", component).custom_attrs)


def event_triggers(component: BaseComponent) -> dict[str, Any]:
    """Return ``component.event_triggers`` typed as ``dict[str, Any]``."""
    return cast("dict[str, Any]", cast("Any", component).event_triggers)


def el(tag: str, *children: Any, **props: Any) -> Component:  # noqa: ANN401
    """Build ``rx.el.<tag>(*children, **props)`` typed as ``Component``.

    Reflex's element factories are partially unknown to pyright; this keeps the
    cast in one place.
    """
    import reflex as rx  # noqa: PLC0415

    factory = getattr(rx.el, tag)
    return cast("Component", factory(*children, **props))


def chain_events(chain: object) -> list[Any]:
    """Return ``chain.events`` (an ``EventChain``) typed as ``list[Any]``."""
    return list(cast("Any", chain).events)
