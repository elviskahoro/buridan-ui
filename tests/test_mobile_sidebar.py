"""Regression coverage for the mobile sidebar dropdown's per-route link dispatch.

The mobile ``mobile_menu`` (rendered for ``< md`` viewports) previously routed
every ``SIDEBAR_SECTIONS`` entry through a single ``rx.el.a(..., to=f"/{route['url']}")``
branch. For the external ``pypi 0.1.19`` entry this produced
``to="/https://pypi.org/project/buridan-create/"`` with no ``reload_document``,
i.e. client-side routing to an unregistered in-app pathname that the catch-all
404 route renders. The companion desktop renderer ``create_menu_item`` was
already fixed to special-case external (pypi) and static-asset (llms.txt) links;
this module pins the same behaviour for the mobile menu and guards against the
mobile/desktop divergence recurring.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.templates.docsidebar import (
    SIDEBAR_SECTIONS,
    _mobile_menu_link,
    create_menu_item,
    mobile_menu,
)

PYPI_ROUTE = {"title": "pypi 0.1.19", "url": "https://pypi.org/project/buridan-create/"}
LLMS_ROUTE = {"title": "llms.txt", "url": "llms.txt"}
INTERNAL_ROUTE = {
    "title": "Introduction",
    "url": "docs/getting-started/introduction",
}


def test_pypi_mobile_link_navigates_externally_with_document_reload() -> None:
    link = _mobile_menu_link(PYPI_ROUTE)
    rendered = str(link)

    assert "reloadDocument:true" in rendered
    assert 'to:"https://pypi.org/project/buridan-create/"' in rendered
    assert 'to:"/https://pypi.org/project/buridan-create/"' not in rendered
    assert 'to:"/https' not in rendered


def test_llms_txt_mobile_link_uses_document_navigation_to_static_asset() -> None:
    link = _mobile_menu_link(LLMS_ROUTE)
    rendered = str(link)

    assert "reloadDocument:true" in rendered
    assert 'to:"/llms.txt"' in rendered


def test_internal_mobile_link_uses_client_side_routing() -> None:
    link = _mobile_menu_link(INTERNAL_ROUTE)
    rendered = str(link)

    assert "reloadDocument" not in rendered
    assert 'to:"/docs/getting-started/introduction"' in rendered


def test_mobile_menu_has_no_malformed_external_client_side_paths() -> None:
    """No external URL in SIDEBAR_SECTIONS may be client-routed to an in-app path."""
    rendered = str(mobile_menu())

    assert 'to:"/https' not in rendered
    assert 'to:"/http://' not in rendered
    for section in SIDEBAR_SECTIONS:
        for route in section.routes:
            url = route["url"]
            if url.startswith(("http://", "https://")):
                assert f'to:"/{url}"' not in rendered


def test_mobile_pypi_entry_matches_desktop_create_menu_item_navigation_props() -> None:
    mobile_rendered = str(_mobile_menu_link(PYPI_ROUTE))
    desktop_rendered = str(create_menu_item(PYPI_ROUTE))

    for needle in (
        "reloadDocument:true",
        'to:"https://pypi.org/project/buridan-create/"',
    ):
        assert needle in mobile_rendered
        assert needle in desktop_rendered


def test_mobile_llms_txt_entry_matches_desktop_create_menu_item_navigation_props() -> (
    None
):
    mobile_rendered = str(_mobile_menu_link(LLMS_ROUTE))
    desktop_rendered = str(create_menu_item(LLMS_ROUTE))

    for needle in ("reloadDocument:true", 'to:"/llms.txt"'):
        assert needle in mobile_rendered
        assert needle in desktop_rendered
