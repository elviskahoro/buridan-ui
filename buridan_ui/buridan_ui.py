import reflex as rx

from buridan_ui.landing.hero import hero

from buridan_ui.static.routes import PantryRoutes, ChartRoutes
from buridan_ui.static.meta import ChartMetaData, PantryMetaData

from buridan_ui.start.flexgen import flexgen
from buridan_ui.start.buridan import buridan
from buridan_ui.start.charting import charting
from buridan_ui.start.installation import installation
from buridan_ui.start.introduction import introduction
from buridan_ui.start.changelog.changelog import changelog

from buridan_ui.wrappers.base.main import base
from buridan_ui.config import SiteTheme, SiteMetaTags
from buridan_ui.templates.settings.settings import SiteThemeColor
from buridan_ui.export import pantry_exports_config, charts_exports_config

app = rx.App(
    theme=rx.theme(appearance=SiteTheme, accent_color=SiteThemeColor.value),
    stylesheets=["css/globals.css"],
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
    parent_dir: str,
) -> None:
    metadata_source = ChartMetaData if parent_dir == "charts" else PantryMetaData

    for route in routes:
        dir_meta = metadata_source[route["dir"]]

        @base(route["path"], route["name"], dir_meta)
        def export_page() -> callable:
            return get_exports(route["dir"], export_config)

        app.add_page(
            export_page(),
            route=route["path"],
            title=f"{route['name']} - Buridan UI",
            image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
            meta=SiteMetaTags,
        )


add_routes(ChartRoutes, charts_exports_config, "charts")
add_routes(PantryRoutes, pantry_exports_config, "pantry")

app.add_page(
    hero(),
    route="/",
    title="Buridan Stack",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    buridan(),
    route="/getting-started/who-is-buridan",
    title="Who Is Buridan - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    changelog(),
    route="/getting-started/changelog",
    title="Changelog - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    introduction(),
    route="/getting-started/introduction",
    title="Introduction - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    installation(),
    route="/getting-started/installation",
    title="Installation - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    charting(),
    route="/getting-started/charting",
    title="Charting - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
app.add_page(
    flexgen(),
    route="/getting-started/flexgen",
    title="Flexgen - Buridan UI",
    image="https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG",
    meta=SiteMetaTags,
)
