import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx

from app.utils.links import external_link, is_external_href
from app.www.style import markdown_component_map


def test_external_link_uses_document_navigation_and_preserves_attributes() -> None:
    link = external_link(
        "GitHub",
        href="https://github.com/LineIndent/ui",
        target="_blank",
        rel="noopener noreferrer",
        class_name="no-underline",
    )

    assert "reloadDocument:true" in str(link)
    assert 'target:"_blank"' in str(link)
    assert 'rel:"noopener noreferrer"' in str(link)
    assert "no-underline" in str(link.class_name)
    assert "https://github.com/LineIndent/ui" in str(link.to)


def test_external_blank_link_defaults_to_safe_rel() -> None:
    link = external_link("External", href="https://example.com", target="_blank")

    assert 'rel:"noopener noreferrer"' in str(link)


def test_external_link_preserves_explicit_navigation_and_rel_props() -> None:
    link = external_link(
        "External",
        href="https://example.com",
        target="_blank",
        rel="noreferrer",
        reload_document=False,
    )

    assert "reloadDocument:false" in str(link)
    assert 'rel:"noreferrer"' in str(link)


def test_markdown_component_map_receives_runtime_href_as_native_link_props() -> None:
    markdown = rx.markdown(
        "[External](https://example.com/docs)",
        component_map=markdown_component_map,
    )
    markdown_component = markdown.children[0]
    link_component = markdown_component.get_component("a")
    link_renderer = str(markdown_component.format_component_map()["a"])

    assert str(link_component.href) == '"#"'
    assert not hasattr(link_component, "to")
    assert not hasattr(link_component, "reload_document")
    assert "...props" in link_renderer
    assert 'href:"#"' in link_renderer
    assert "reloadDocument" not in link_renderer


def test_is_external_href_handles_http_https_and_internal_urls() -> None:
    assert is_external_href("http://example.com") is True
    assert is_external_href("https://example.com") is True
    assert is_external_href("HTTPS://example.com") is True
    assert is_external_href("/docs/getting-started") is False
    assert is_external_href("#installation") is False
    assert is_external_href(None) is False
