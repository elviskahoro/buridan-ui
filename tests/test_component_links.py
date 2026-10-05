from app.pages.components import _get_component_link_data
from app.utils.routes import ALL_ROUTES


def test_component_links_resolve_to_documentation_routes() -> None:
    """Every generated component link must have a corresponding docs route."""
    links = _get_component_link_data()
    component_urls = {route["url"] for route in ALL_ROUTES["components"]}
    broken = [
        {"label": name, "href": f"docs/components/{slug}"}
        for name, slug in links
        if f"docs/components/{slug}" not in component_urls
    ]

    assert not broken, f"Component links without documentation routes: {broken}"
    assert ("Core", "core") not in links
    assert ("Chart", "chart") in links
