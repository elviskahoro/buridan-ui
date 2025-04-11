import reflex as rx

from buridan_ui.landing.hero import hero
from buridan_ui.static.routes import ChartRoutes, PantryRoutes
from buridan_ui.static.meta import ChartMetaData, PantryMetaData
from buridan_ui.start.flexgen import flexgen
from buridan_ui.start.buridan import buridan
from buridan_ui.start.charting import charting
from buridan_ui.start.installation import installation
from buridan_ui.start.introduction import introduction
from buridan_ui.start.changelog.changelog import changelog

from buridan_ui.wrappers.base.main import base
from buridan_ui.config import SiteTheme, SiteMetaTags, FontFamily
from buridan_ui.templates.settings.settings import SiteThemeColor
from buridan_ui.export import (
    charts_exports_config,
    pantry_exports_config,
    filter_routes,
)

# Base configuration
BASE_IMAGE_URL = "https://raw.githubusercontent.com/buridan-ui/ui/refs/heads/main/assets/new_logo.PNG"

# Create app with consistent styling
app = rx.App(
    theme=rx.theme(appearance=SiteTheme, accent_color=SiteThemeColor.value),
    stylesheets=["/css/globals.css"],
    style={
        rx.heading: {"font_family": FontFamily},
        rx.text: {"font_family": FontFamily},
        rx.el.label: {"font_family": FontFamily},
    },
)


def get_exports(directory: str, config_file: dict[str, list[callable]]):
    return [export for export in config_file[directory]]


# def add_routes(
#     routes: list[dict[str, str]],
#     export_config: dict[str, list[callable]],
#     parent_dir: str,
# ) -> None:
#     metadata_source = ChartMetaData if parent_dir == "charts" else PantryMetaData
#
#     for _route in routes:
#         dir_meta = metadata_source[_route["dir"]]
#
#         @base(_route["path"], _route["name"], dir_meta)
#         def export_page() -> callable:
#             return get_exports(_route["dir"], export_config)
#
#         add_page(export_page(), _route["path"], f"{_route['name']} - Buridan UI")


def add_routes(
    routes: list[dict[str, str]],
    export_config: dict[str, list[callable]],
    parent_dir: str,
) -> None:
    metadata_source = ChartMetaData if parent_dir == "charts" else PantryMetaData

    # Filter the routes based on development settings
    filtered_routes = filter_routes(routes)

    for _route in filtered_routes:
        dir_meta = metadata_source[_route["dir"]]

        @base(_route["path"], _route["name"], dir_meta)
        def export_page() -> callable:
            return get_exports(_route["dir"], export_config)

        add_page(export_page(), _route["path"], f"{_route['name']} - Buridan UI")


def add_page(page_component, route_path, title):
    """Helper function to add pages with consistent metadata"""
    app.add_page(
        page_component,
        route=route_path,
        title=title,
        image=BASE_IMAGE_URL,
        meta=SiteMetaTags,
    )


# Add dynamic routes from configurations
add_routes(ChartRoutes, charts_exports_config, "charts")
add_routes(PantryRoutes, pantry_exports_config, "pantry")

# Define static routes with consistent structure
STATIC_ROUTES = [
    {
        "path": "/",
        "component": hero,
        "title": "Buridan Stack",
    },
    {
        "path": "/getting-started/who-is-buridan",
        "component": buridan,
        "title": "Who Is Buridan - Buridan UI",
    },
    {
        "path": "/getting-started/changelog",
        "component": changelog,
        "title": "Changelog - Buridan UI",
    },
    {
        "path": "/getting-started/introduction",
        "component": introduction,
        "title": "Introduction - Buridan UI",
    },
    {
        "path": "/getting-started/installation",
        "component": installation,
        "title": "Installation - Buridan UI",
    },
    {
        "path": "/getting-started/charting",
        "component": charting,
        "title": "Charting - Buridan UI",
    },
    {
        "path": "/getting-started/flexgen",
        "component": flexgen,
        "title": "Flexgen - Buridan UI",
    },
]

# Add static routes
for route in STATIC_ROUTES:
    add_page(route["component"](), route["path"], route["title"])
