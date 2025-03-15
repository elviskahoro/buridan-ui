import reflex as rx

from .landing.hero import hero
from .templates.settings.settings import SiteThemeColor
from .wrappers.base.main import base

from .start.buridan import buridan
from .start.installation import installation
from .start.introduction import introduction
from .start.changelog.changelog import changelog

from buridan_ui.export import pantry_exports_config, charts_exports_config
from buridan_ui.static.routes import PantryRoutes, ChartRoutes
from buridan_ui.config import SiteTheme, SiteMetaTags


app = rx.App(
    theme=rx.theme(appearance=SiteTheme, accent_color=SiteThemeColor.value),
    style={
        rx.heading: {"font_family": "IBM Plex Mono,ui-monospace,monospace"},
        rx.text: {"font_family": "IBM Plex Mono,ui-monospace,monospace"},
        rx.el.label: {"font_family": "IBM Plex Mono,ui-monospace,monospace"},
    },
)


def get_exports(directory: str, config_file: dict[str, list[callable]]):
    return [export for export in config_file[directory]]


def add_routes(
    routes: list[dict[str, str]],
    export_config: dict[str, list[callable]],
) -> None:
    for route in routes:

        @base(route["path"], route["name"])
        def export_page() -> callable:
            return get_exports(route["dir"], export_config)

        app.add_page(
            export_page(),
            route=route["path"],
            title=f"{route['name']} - Buridan UI",
            image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
            meta=SiteMetaTags,
        )


app.add_page(
    hero(),
    route="/",
    title=f"Buridan Collection",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)

add_routes(PantryRoutes, pantry_exports_config)
add_routes(ChartRoutes, charts_exports_config)
app.add_page(
    buridan(),
    route="/getting-started/who-is-buridan",
    title=f"Who Is Buridan - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    changelog(),
    route="/getting-started/changelog",
    title=f"Changelog - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    introduction(),
    route="/getting-started/introduction",
    title=f"Introduction - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    installation(),
    route="/getting-started/installation",
    title=f"Installation - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
