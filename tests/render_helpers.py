"""Typed wrappers around Reflex's bare-``dict`` ``Component.render()``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from reflex.components.component import BaseComponent


def render_dict(component: BaseComponent) -> dict[str, Any]:
    """Return ``component.render()`` typed as ``dict[str, Any]``."""
    return cast("dict[str, Any]", component.render())


def render_props(component: BaseComponent) -> list[str]:
    """Return the rendered ``props`` list of ``component`` as strings."""
    return [str(p) for p in cast("list[Any]", render_dict(component)["props"])]


def render_text(component: BaseComponent) -> str:
    """Return ``str(component.render())``."""
    return str(render_dict(component))
