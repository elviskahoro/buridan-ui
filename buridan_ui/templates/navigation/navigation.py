from __future__ import annotations

import reflex as rx
from reflex.constants.colors import Color

from .style import NavigationStyle
from ..drawer.drawer import drawer
from buridan_ui.static.routes import NavigationRoutes
from ...ui.atoms.buttons import button_with_link, theme_button


def navigation_links(data: dict[str, str | Color]):
    return rx.link(
        rx.text(data["name"], size="1", weight="medium", color=rx.color("slate", 12)),
        href=data["path"],
        text_decoration="none",
    )


def navigation_left_side_items():
    return rx.hstack(
        rx.link(
            rx.el.label(
                f"buridan/ui",
                class_name="text-sm font-bold font-sans flex items-center align-center gap-x-2 "
                + rx.color_mode_cond("text-slate-700", "text-slate-200"),
            ),
            text_decoration="none",
            href="/",
        ),
        rx.divider(width="0.75em", opacity="0"),
        rx.hstack(
            rx.foreach(NavigationRoutes, navigation_links),
            display=["none", "none", "none", "none", "flex", "flex"],
            align="center",
        ),
        align="center",
        spacing="2",
    )


def landing_page_navigation():
    return rx.hstack(
        navigation_left_side_items(),
        rx.el.div(
            theme_button(),
            button_with_link("github", "https://github.com/buridan-ui/ui"),
            class_name="flex flex-row gap-x-2",
            display=["none" if i <= 3 else "flex" for i in range(6)],
        ),
        rx.box(
            drawer(),
            display=["flex" if i <= 3 else "none" for i in range(6)],
        ),
        **NavigationStyle.landing_page_nav,
    )
