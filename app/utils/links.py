from typing import Any

import reflex as rx


def is_external_href(href: Any) -> bool:
    """Return whether a known href is an HTTP(S) URL."""
    return isinstance(href, str) and href.lower().startswith(("http://", "https://"))


def external_link(*children: Any, href: str, **props: Any) -> rx.Component:
    """Create a link that lets the browser navigate to an external URL."""
    props.setdefault("reload_document", True)
    if props.get("target") == "_blank":
        props.setdefault("rel", "noopener noreferrer")
    return rx.el.a(*children, href=href, **props)
