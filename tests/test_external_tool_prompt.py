import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote_plus, urlparse

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.templates.toc import _create_external_tool_links


def _rendered(url: str = "docs/components/button") -> str:
    return json.dumps(_create_external_tool_links(url).render(), default=str)


def _extract_href(rendered: str, host: str) -> str:
    """Pull the first URL value for ``host`` out of the component JSON dump.

    Reflex renders external-link hrefs on a ``to`` prop (it maps ``href`` to
    Next.js ``to``), while internal links keep ``href``; accept either.
    """
    match = re.search(
        rf"(?:(?:to|href):\\?\"|\")?(https://{re.escape(host)}[^\"\\]*)", rendered
    )
    assert match, f"{host} href not found in rendered output"
    return match.group(1)


def test_external_tool_href_has_no_raw_newlines_or_indent_leak() -> None:
    """The emitted ChatGPT href must not embed a raw newline or the
    four-space indentation run that the source f-string used to leak."""
    rendered = _rendered()
    chatgpt = rendered[rendered.find("chatgpt") : rendered.find("chatgpt") + 400]
    assert "\\n" not in chatgpt and "    Help" not in chatgpt, (
        "external-tool prompt leaked source newlines/indentation into the URL"
    )


def test_external_tool_hrefs_are_percent_encoded_and_decode_to_clean_prompt() -> None:
    """All three "Open in …" hrefs must be valid RFC-3986 URIs whose
    percent-decoded prompt is the single-line sentence — no raw whitespace
    in the query, no source-indentation runs, and ``fmt_url`` embedded per
    page. Guards against both re-introducing the multi-line leak and dropping
    the ``quote()`` call.
    """
    for page in (
        "docs/components/button",
        "docs/getting-started",
        "docs/components/accordion",
    ):
        rendered = _rendered(page)
        for host in ("chatgpt.com", "claude.ai", "build.reflex.dev"):
            href = _extract_href(rendered, host)
            parsed = urlparse(href)
            assert parsed.scheme == "https"
            assert parsed.netloc == host
            # RFC 3986: query must not contain raw whitespace.
            for ch in (" ", "\n", "\t", "\r"):
                assert ch not in parsed.query, f"{host}: raw {ch!r} in query"
            # Spaces must be percent-encoded, not raw.
            assert "%20" in href, f"{host}: prompt is not percent-encoded"
            decoded = unquote_plus(parsed.query)
            assert "\n" not in decoded
            assert "    " not in decoded, f"{host}: source-indentation leaked"
            assert decoded == decoded.strip(), (
                f"{host}: prompt has surrounding whitespace"
            )
            assert f"https://buridan-ui.reflex.run/{page}" in decoded, (
                f"{host}: fmt_url for {page} not in decoded prompt"
            )
