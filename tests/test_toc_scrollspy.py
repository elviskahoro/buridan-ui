import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
TOC_TEMPLATE = ROOT_DIR / "app" / "templates" / "toc.py"


def _set_active_body() -> str:
    """Return the source of the scrollspy ``setActive`` function."""
    source = TOC_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"function setActive\(id\)\s*\{(.*?)\n\s*\}\n", source, re.DOTALL)
    assert match, "setActive(id) not found in toc.py"
    return match.group(1)


def test_scrollspy_matches_href_exactly_for_prefix_collisions() -> None:
    """``dev`` must not activate ``#dev.py``: compare hrefs exactly, no selectors."""
    body = _set_active_body()

    # Exact comparison of the href attribute against "#" + id (either operand order).
    exact = (
        r"""getAttribute\(\s*['"]href['"]\s*\)\s*===\s*(['"])#\1\s*\+\s*id\b"""
        r"""|(['"])#\2\s*\+\s*id\s*===\s*\w+\.getAttribute\(\s*['"]href['"]\s*\)"""
    )
    assert re.search(exact, body)


def test_scrollspy_does_not_interpolate_id_into_selector_or_fuzzy_match() -> None:
    body = _set_active_body()

    # No CSS selector lookups built from the heading id (ids may contain "." etc.).
    assert not re.search(r"querySelector(All)?\s*\(", body)
    # No substring/prefix/suffix matching on hrefs.
    assert not re.search(r"\[href\s*[*^$|~]?=", body)
    assert not re.search(r"\.(includes|indexOf|startsWith|endsWith)\s*\(", body)
