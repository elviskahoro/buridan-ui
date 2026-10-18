# noqa: INP001
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

from app.templates.docsidebar import (  # noqa: E402
    SIDEBAR_SECTIONS,
    _mobile_menu_link,  # pyright: ignore[reportPrivateUsage]
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


GITHUB_ROUTE = {
    "title": "GitHub",
    "url": "https://github.com/elviskahoro/buridan-ui",
}


def test_non_pypi_titled_external_link_dispatches_on_url() -> None:
    """External dispatch must key on the URL, not the title.

    A non-pypi-titled external route (e.g. a GitHub link) must still route
    via document reload. Reverting the dispatch to ``title.startswith("pypi")``
    would drop this route into the generic client-side branch and render
    ``to:"/https://..."`` — the exact in-app-404 bug this PR fixes — so this
    case makes the suite discriminate the URL-keyed dispatch for both
    ``_mobile_menu_link`` and ``create_menu_item``.
    """
    for rendered in (
        str(_mobile_menu_link(GITHUB_ROUTE)),
        str(create_menu_item(GITHUB_ROUTE)),
    ):
        assert "reloadDocument:true" in rendered
        assert 'to:"https://github.com/elviskahoro/buridan-ui"' in rendered
        assert 'to:"/https' not in rendered
