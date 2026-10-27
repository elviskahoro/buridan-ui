"""Regression coverage for the docs heading-id deduplication pipeline.

The docs site builds every component documentation page from markdown in three
stages:

* ``app/www/generator.py`` extracts the page's h1/h2 headings into TOC data,
* ``app/www/style.py`` renders those headings into DOM elements (with ids),
* ``app/templates/toc.py`` renders the "On This Page" TOC links + scrollspy.

When two headings normalize to the same slug (e.g. ``# Badge`` and ``## badge``
both slug to ``badge``) the pre-fix pipeline produced a duplicate DOM id and two
TOC entries both linking to ``#badge``; the browser ``getElementById('badge')``
always resolved to the first match (the page-top h1), so the API Reference TOC
entry scrolled to the top of the page and could never receive the scrollspy
highlight. The fix deduplicates slugs server-side via a shared
:class:`HeadingIdRegistry` consumed by both the TOC extractor and the rendered
DOM, so the TOC href fragments and the rendered heading DOM ids always match
exactly one element per section (``badge``, ``badge-1``).

These tests pin the contracts most likely to regress silently: the registry's
case-insensitive dedup, the two-phase (TOC + DOM) sync, code-fence-aware
heading extraction, the end-to-end pipeline, the all-docs scope guard, and the
TOC href shape.
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.templates.toc import (  # noqa: E402
    _create_markdown_toc_links,  # pyright: ignore[reportPrivateUsage]
)
from app.www.generator import generate_docs_library  # noqa: E402
from app.www.parser import DocParser  # noqa: E402
from app.www.style import (  # noqa: E402
    HeadingIdRegistry,
    iter_heading_segments,
)

TOC_TEMPLATE = ROOT_DIR / "app" / "templates" / "toc.py"


def test_registry_suffixes_case_insensitive_collisions() -> None:
    # The exact Badge-page collision: `# Badge` and `## badge` both slug to
    # `badge`. The registry must keep the first and suffix the second (and keep
    # suffixing for any further case variants).
    reg = HeadingIdRegistry()
    assert reg.register("Badge") == "badge"
    assert reg.register("badge") == "badge-1"
    assert reg.register("BADGE") == "badge-2"


def test_registry_next_id_consumes_in_document_order() -> None:
    # register() (TOC build) and next_id() (DOM render) traverse the page in the
    # same document order, so a heading that repeats gets the slugs in order.
    # If this two-phase sync breaks, the TOC href fragment and the rendered DOM
    # id silently disagree and the scrollspy/click target desyncs.
    reg = HeadingIdRegistry()
    reg.register("Badge")
    reg.register("badge")

    assert reg.next_id("Badge") == "badge"
    assert reg.next_id("badge") == "badge-1"


def test_iter_heading_segments_ignores_hash_lines_inside_code_fence() -> None:
    # A `#`-comment inside a ``` fence is code, not a heading. Without this,
    # the generator's TOC extractor and rx.markdown would disagree on the set
    # of headings and the registry's two phases (TOC vs DOM) would desync — a
    # silent regression that would re-introduce duplicate ids.
    chunk = "```python\n# this is a comment, not a heading\nprint('x')\n```\n## Real"
    segments = list(iter_heading_segments(chunk))
    headings = [s for s in segments if s[0] == "heading"]
    assert headings == [("heading", (2, "Real"))]


def test_parse_and_render_dedups_case_insensitive_heading_collision() -> None:
    # The reported scenario: `# Badge` and `## badge` both slug to `badge`. The
    # DOM must end up with two distinct ids (`badge` and `badge-1`), not a
    # duplicate `badge`, and the ids must be plain server-computed strings (no
    # client-side `toLowerCase()`/`replaceAll()` JS expression that hides the
    # collision from server-side checks).
    parser = DocParser()
    reg = HeadingIdRegistry()
    reg.register("Badge")
    reg.register("badge")

    components = parser.parse_and_render(
        "# Badge\n\ntext\n\n## badge\n\nmore text",
        heading_registry=reg,
    )

    rendered = "\n".join(str(c) for c in components)
    assert rendered.count('id:"badge"') == 1
    assert 'id:"badge-1"' in rendered
    assert "toLowerCase" not in rendered
    assert "replaceAll" not in rendered


def test_generator_toc_href_fragments_match_rendered_dom_ids() -> None:
    # End-to-end: every TOC href fragment must resolve to exactly one rendered
    # DOM heading id, so the scrollspy's getElementById never silently resolves
    # a duplicate to the first match. Guards the whole generator+parser pipeline
    # on the reported Badge page.
    docs = generate_docs_library()
    badge = next(doc for doc in docs if doc.url == "docs/components/badge")

    toc_slugs = {entry["id"] for entry in badge.table_of_content}
    dom_ids: set[str] = set()
    for component in badge.component:
        dom_ids.update(re.findall(r'id:"([^"]+)"', str(component)))

    missing = toc_slugs - dom_ids
    assert not missing, f"TOC slugs with no matching DOM heading: {missing}"

    # And the exact collision is resolved: `Badge` keeps `badge`, the lowercase
    # `badge` API-Reference heading becomes `badge-1`.
    by_text = {entry["text"]: entry["id"] for entry in badge.table_of_content}
    assert by_text["Badge"] == "badge"
    assert by_text["badge"] == "badge-1"


def test_no_doc_page_has_duplicate_heading_ids() -> None:
    # Scope guard: the dedup must hold across every doc page, not just badge.
    # Each TOC slug must also resolve to exactly one rendered DOM heading id on
    # the page, so the TOC↔DOM agreement the badge test pins is not silently
    # lost on the other pages. Only TOC slugs are asserted — non-heading
    # component ids legitimately repeat in page bodies (e.g. chart demos
    # serialize `id:"desktop"` more than once).
    docs = generate_docs_library()
    offenders: list[str] = []
    for doc in docs:
        toc_ids = [entry["id"] for entry in doc.table_of_content]
        if len(toc_ids) != len(set(toc_ids)):
            offenders.append(doc.url)
            continue
        dom_ids: list[str] = []
        for component in doc.component:
            dom_ids.extend(re.findall(r'id:"([^"]+)"', str(component)))
        for slug in toc_ids:
            if dom_ids.count(slug) != 1:
                offenders.append(f"{doc.url} (slug {slug!r}: {dom_ids.count(slug)} DOM hits)")
    assert not offenders, f"pages with duplicate or unmatched TOC ids: {offenders}"


def test_toc_links_href_uses_precomputed_slug_verbatim() -> None:
    # The pre-fix toc.py re-derived the slug from the raw heading text with
    # `entry['id'].lower().replace(' ', '-')`, which re-introduced the collision
    # even when ids had been deduped. The href must use the pre-computed slug
    # verbatim, and the re-slugify call must not come back.
    toc_data = [
        {"text": "Badge", "id": "badge", "level": 1},
        {"text": "badge", "id": "badge-1", "level": 2},
    ]
    rendered = str(_create_markdown_toc_links("docs/components/badge", toc_data))

    hrefs = re.findall(r'to:"#([^"]+)"', rendered)
    assert hrefs == ["badge", "badge-1"]

    source = TOC_TEMPLATE.read_text(encoding="utf-8")
    assert "entry['id'].lower().replace(' ', '-')" not in source
