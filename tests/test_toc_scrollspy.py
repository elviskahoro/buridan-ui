"""Regression coverage for the documentation TOC scrollspy highlight.

The scrollspy lives in ``app/templates/toc.py`` as an inline JS string rendered
through Reflex's ``rx.el.a`` (a React Router ``<Link>``). React Router renders a
hash-only ``to`` (e.g. ``"#dev"``) as an ``<a>`` whose ``href`` is the path-prefixed
URL of the current page (e.g. ``/docs/getting-started/dev#dev``), so ``setActive``
must compare the rendered ``href``'s trailing fragment against the heading id
rather than the bare ``"#" + id``.

These tests guard that contract with both static source-shape assertions and a
jsdom + react-router-dom runtime harness that exercises the *real* ``setActive``
source extracted from ``toc.py`` against the production-rendered hrefs. The
runtime harness is what catches regressions: under the pre-fix exact-``===``
comparison nothing highlights, and under the original substring selector the
``dev``-vs-``dev.py`` prefix collision (#75) reappears when ``#dev.py`` precedes
``#dev`` in document order.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parent.parent
TOC_TEMPLATE = ROOT_DIR / "app" / "templates" / "toc.py"
REPRO_DIR = Path(__file__).parent / "toc_scrollspy_repro"


def _set_active_body() -> str:
    """Return the source of the scrollspy ``setActive`` function body.

    Mirrors the extraction the original tests used: everything between
    ``function setActive(id) {`` and its closing ``}`` line.
    """
    source = TOC_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"function setActive\(id\)\s*\{(.*?)\n\s*\}\n", source, re.DOTALL)
    assert match, "setActive(id) not found in toc.py"
    return match.group(1)


def _set_active_full_source() -> str:
    """Return the full ``function setActive(id) { ... }`` declaration.

    Used to feed the *real* scrollspy implementation into the runtime harness so
    a revert of the fix turns the runtime test red. Brace-matched extraction
    stays valid even if the body later grows inner brace blocks.
    """
    source = TOC_TEMPLATE.read_text(encoding="utf-8")
    start = source.index("function setActive(id)")
    open_brace = source.index("{", start)
    depth = 0
    for idx in range(open_brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]
    raise AssertionError("unterminated setActive function in toc.py")


def test_scrollspy_compares_rendered_href_fragment_against_id() -> None:
    """``setActive`` must compare the rendered href's trailing fragment, not ``"#" + id``.

    React Router renders ``<Link to="#dev">`` as ``<a href="/path#dev">``, so the
    full href never equals the bare fragment ``"#dev"``. The fix compares the
    fragment after the ``#`` against ``id`` (either operand order), which also
    preserves the exact-match semantics needed so ``dev`` does not activate
    ``#dev.py``.
    """
    body = _set_active_body()

    fragment = r"getAttribute\(\s*['\"]href['\"]\s*\)\s*\.split\(\s*['\"]#['\"]\s*\)\s*\[\s*1\s*\]"
    assert re.search(fragment + r"\s*===\s*id\b", body) or re.search(
        r"\bid\b\s*===\s*" + fragment, body
    ), (
        "setActive must compare getAttribute('href').split('#')[1] against id "
        "(React Router renders a path-prefixed href; === '#' + id never matches)."
    )

    # The buggy exact comparison against a bare fragment must NOT remain.
    assert not re.search(
        r"getAttribute\(\s*['\"]href['\"]\s*\)\s*===\s*['\"]#['\"]\s*\+\s*id\b", body
    ), "setActive must not compare the full rendered href against '#' + id."


def test_scrollspy_does_not_interpolate_id_into_selector_or_fuzzy_match() -> None:
    body = _set_active_body()

    # No CSS selector lookups built from the heading id (ids may contain "." etc.).
    assert not re.search(r"querySelector(All)?\s*\(", body)
    # No substring/prefix/suffix/attribute selectors on hrefs.
    assert not re.search(r"\[href\s*[*^$|~]?=", body)
    assert not re.search(r"\.(includes|indexOf|startsWith|endsWith)\s*\(", body)


def test_scrollspy_runtime_highlight_under_react_router() -> None:
    """Render the real ``setActive`` against production-shape React Router hrefs.

    Renders ``<Link to="#dev.py">`` *before* ``<Link to="#dev">`` (the ordering
    that exposes the #75 prefix collision) under ``react-router-dom@7`` in jsdom
    at the production docs pathname, then runs the actual ``setActive`` source
    pulled from ``toc.py`` and asserts which ``.toc-link`` is highlighted.

    Preconditions: Node.js and the JS deps installed in
    ``tests/toc_scrollspy_repro/node_modules`` (run ``npm ci`` in that
    directory). The test is skipped, not failed, when the toolchain is absent.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to run the scrollspy runtime harness")
    if not (REPRO_DIR / "node_modules").is_dir():
        pytest.skip(
            f"run `npm ci` in {REPRO_DIR} to install the jsdom/react-router harness"
        )

    js = _RUNTIME_HARNESS.replace("__SETACTIVE_SRC__", _set_active_full_source())
    result = subprocess.run(
        [node, "-e", js],
        cwd=str(REPRO_DIR),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"runtime harness failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert result.stderr.strip() == "", f"unexpected stderr:\n{result.stderr}"

    payload = json.loads(result.stdout)

    # React Router renders path-prefixed hrefs; this is the premise the fix
    # depends on and the thing a bare-fragment comparison would miss.
    rendered = payload["rendered"]
    assert len(rendered) == 2
    by_text = {link["text"]: link["href"] for link in rendered}
    assert by_text["devpytoc"] == "/docs/getting-started/dev#dev.py"
    assert by_text["devtoc"] == "/docs/getting-started/dev#dev"

    # dev (placed after dev.py) must highlight the #dev link and NOT #dev.py.
    # - pre-fix `=== '#' + id`: nothing matches a path-prefixed href -> null.
    # - original substring selector: #dev.py precedes #dev, so "dev" matches
    #   #dev.py first -> "devpytoc" (the #75 collision).
    assert payload["after_dev"] == "devtoc"
    assert payload["after_devpy"] == "devpytoc"


_RUNTIME_HARNESS = r"""
const { JSDOM } = require("jsdom");
const dom = new JSDOM(
  '<!DOCTYPE html><html><body><div id="root"></div></body></html>',
  { url: "https://example.com/docs/getting-started/dev" }
);
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.navigator = dom.window.navigator;
globalThis.history = dom.window.history;
globalThis.location = dom.window.location;

const React = require("react");
const { createRoot } = require("react-dom/client");
const { createBrowserRouter, RouterProvider, Link } = require("react-router-dom");

// #dev.py is deliberately placed BEFORE #dev so a substring/prefix matcher
// (`.toc-link[href*="#dev"]`) would select #dev.py first for id "dev" — the
// exact prefix collision #75 was fixing.
const routes = [{
  path: "/docs/getting-started/dev",
  element: React.createElement("div", null,
    React.createElement(Link, { to: "#dev.py", className: "toc-link" }, "devpytoc"),
    React.createElement("span", null, " "),
    React.createElement(Link, { to: "#dev", className: "toc-link" }, "devtoc"))
}];
const router = createBrowserRouter(routes);
createRoot(document.getElementById("root")).render(
  React.createElement(RouterProvider, { router })
);

setTimeout(() => {
  const links = document.querySelectorAll(".toc-link");
  const rendered = Array.from(links).map((a) => ({
    text: a.textContent,
    href: a.getAttribute("href"),
  }));

  __SETACTIVE_SRC__

  function activeNow() {
    const a = document.querySelector('.toc-link[data-active="true"]');
    return a ? a.textContent : null;
  }

  setActive("dev");
  const after_dev = activeNow();
  setActive("dev.py");
  const after_devpy = activeNow();

  console.log(JSON.stringify({ rendered, after_dev, after_devpy }));
}, 200);
"""
