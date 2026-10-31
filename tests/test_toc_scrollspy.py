"""Regression coverage for the documentation TOC scrollspy highlight and lifecycle.

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

A second group of tests covers the scrollspy *lifecycle* bug introduced by the
same commit (b350a85): the ``MutationObserver`` (``domWatcher``) was left
connected after the synchronous ``initScrollspy()`` succeeded at mount, so the
next DOM mutation (e.g. ``Prism.highlightAll()``, the copy-button icon swap,
tooltip portals) re-ran the entire ``initScrollspy()``, stacking duplicate click
handlers (each issuing its own ``history.pushState``) and leaking an
``IntersectionObserver`` per re-init. The fix (a) only starts watching when the
synchronous init fails, (b) makes ``initScrollspy()`` idempotent via a
per-instance guard, and (c) tears the watcher / observer / listeners down on
``on_unmount``. The lifecycle is guarded by a jsdom harness that executes the
actual rendered ``on_mount``/``on_unmount`` scripts and asserts one
``pushState`` per click even after DOM mutations, plus component-level checks
that ``on_unmount`` is wired and that each render mints a fresh per-instance
key pair, and a source-shape check that ``initScrollspy`` is idempotent.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT_DIR = Path(__file__).parent.parent
TOC_TEMPLATE = ROOT_DIR / "app" / "templates" / "toc.py"
REPRO_DIR = Path(__file__).parent / "toc_scrollspy_repro"
RENDERED_LINK_COUNT = 2

sys.path.insert(0, str(ROOT_DIR))
from app.templates.toc import (  # noqa: E402
    table_of_content,  # pyright: ignore[reportPrivateUsage]
)


def _set_active_body() -> str:
    """Return the source of the scrollspy ``setActive`` function body.

    Mirrors the extraction the original tests used: everything between
    ``function setActive(id) {`` and its closing ``}`` line.
    """
    source = TOC_TEMPLATE.read_text(encoding="utf-8")
    match = re.search(r"function setActive\(id\)\s*\{(.*?)\n\s*\}\n", source, re.DOTALL)
    msg = "setActive(id) not found in toc.py"
    assert match, msg
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
    msg = "unterminated setActive function in toc.py"
    raise AssertionError(msg)


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
        r"\bid\b\s*===\s*" + fragment,
        body,
    ), (
        "setActive must compare getAttribute('href').split('#')[1] against id "
        "(React Router renders a path-prefixed href; === '#' + id never matches)."
    )

    # The buggy exact comparison against a bare fragment must NOT remain.
    assert not re.search(
        r"getAttribute\(\s*['\"]href['\"]\s*\)\s*===\s*['\"]#['\"]\s*\+\s*id\b",
        body,
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
            f"run `npm ci` in {REPRO_DIR} to install the jsdom/react-router harness",
        )

    assert node is not None
    js = _RUNTIME_HARNESS.replace("__SETACTIVE_SRC__", _set_active_full_source())
    result = subprocess.run(  # noqa: S603
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
    assert len(rendered) == RENDERED_LINK_COUNT
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


# ---------------------------------------------------------------------------
# Scrollspy lifecycle regression coverage (b350a85 follow-up).
#
# The scrollspy on_mount script used to leave its ``MutationObserver``
# (``domWatcher``) connected after the synchronous ``initScrollspy()`` call
# already succeeded at mount, so the next DOM mutation re-ran the whole
# ``initScrollspy()`` and stacked a second set of click handlers (each issuing
# its own ``history.pushState``) plus a second ``IntersectionObserver`` that
# was never disconnected. The fix:
#   1. only starts ``domWatcher.observe(...)`` when the synchronous init fails,
#   2. makes ``initScrollspy()`` idempotent via a per-instance guard, and
#   3. tears the watcher / observer / listeners down on ``on_unmount``.
#
# Static source-shape tests below pin all three layers against the raw
# ``toc.py`` source; the runtime harness executes the *actual* rendered
# ``on_mount``/``on_unmount`` scripts in jsdom and asserts one ``pushState``
# per click even after a DOM mutation, no observer leak, and full cleanup.
# ---------------------------------------------------------------------------

_SENTINEL_INIT = "__TOC_INIT_KEY__"
LIFECYCLE_CLICK_COUNT = 2


def _scrollspy_event_script(toc: Any, key: str) -> str:  # noqa: ANN401
    """Pull the rendered JS string for a lifecycle event from a Reflex component.

    Reflex exposes the ``on_mount``/``on_unmount`` scripts as a deeply nested
    ``LiteralStringVar._var_value`` on ``event_triggers[...].events[0].args[0][1]``.
    The chain is intentionally ``Any``-typed here: the component is the source of
    truth, and what we want is the *exact* string Reflex emits to the client.
    """
    script = toc.event_triggers[key].events[0].args[0][1]._var_value  # noqa: SLF001
    assert isinstance(script, str), f"event {key!r} script must be a string"
    return script


def _rendered_scrollspy_scripts() -> tuple[str, str, str, str]:
    """Render ``table_of_content`` and return the actual on_mount/on_unmount JS.

    Returning the component-rendered strings (with the real per-instance keys
    baked in) means the runtime harness exercises the exact JS Reflex emits,
    not a hand-transcribed copy. A revert of the fix turns the runtime test
    red because the rendered script no longer guards the watcher, etc.

    Returns ``(mount_script, unmount_script, init_key, cleanup_key)`` where the
    keys are the real ``window[...]`` property names baked into both scripts.
    """
    toc: Any = table_of_content(
        "docs/test",
        [
            {"text": "A", "id": "a", "level": 1},
            {"text": "B", "id": "b", "level": 2},
        ],
    )
    mount = _scrollspy_event_script(toc, "on_mount")
    unmount = _scrollspy_event_script(toc, "on_unmount")
    init_key = re.search(r"__tocInit_\w+", mount)
    cleanup_key = re.search(r"__tocCleanup_\w+", mount)
    assert init_key is not None, (
        "rendered on_mount script does not bake in the per-instance init guard"
    )
    assert cleanup_key is not None, (
        "rendered on_mount script does not bake in the per-instance cleanup key"
    )
    assert cleanup_key.group(0) in unmount, (
        "on_unmount script must reference the same cleanup key the on_mount script defines"
    )
    return mount, unmount, init_key.group(0), cleanup_key.group(0)


def test_init_scrollspy_is_idempotent_against_reinit() -> None:
    """``initScrollspy`` must short-circuit once it has fully initialized.

    The bug stacked a second listener set on every re-run. The fix adds a
    per-instance guard so any later call (a still-connected watcher, a manual
    re-invocation, etc.) returns immediately without re-attaching listeners.
    """
    source = TOC_TEMPLATE.read_text(encoding="utf-8")

    assert re.search(
        r"if\s*\(\s*window\[['\"]"
        + re.escape(_SENTINEL_INIT)
        + r"['\"]\]\s*\)\s*return\s+true\s*;",
        source,
    ), "initScrollspy must short-circuit via the per-instance guard"

    # The guard must be SET only after the success preconditions pass, so a
    # failed init (no .toc-link / no sections) can still be retried by the
    # watcher. The set statement must follow the ``if (!sections.length)`` gate.
    sections_gate = source.index("if (!sections.length) return false;")
    guard_set = re.search(
        r"window\[['\"]" + re.escape(_SENTINEL_INIT) + r"['\"]\]\s*=\s*true\s*;",
        source,
    )
    assert guard_set is not None, (
        "initScrollspy must set the per-instance guard once fully initialized"
    )
    assert guard_set.start() > sections_gate, (
        "the per-instance guard must be set after the `if (!sections.length)` "
        "check so a failed init can still be retried by the watcher"
    )


def test_toc_component_declares_on_unmount_that_calls_cleanup() -> None:
    """The ``table_of_content`` component must wire ``on_unmount`` to invoke the
    cleanup function the ``on_mount`` script registered on ``window``.
    """
    mount, unmount, _init_key, cleanup_key = _rendered_scrollspy_scripts()

    # on_unmount must reference the cleanup key and call it as a function.
    assert re.fullmatch(
        rf"\s*if\s*\(\s*window\['{re.escape(cleanup_key)}'\]\s*\)\s*"
        rf"window\['{re.escape(cleanup_key)}'\]\(\)\s*;\s*",
        unmount,
    ), (
        f"on_unmount must be `if (window['{cleanup_key}']) window['{cleanup_key}']();`, got: {unmount!r}"
    )

    # on_mount must actually define that cleanup function on window.
    assert f"window['{cleanup_key}'] = () =>" in mount, (
        "on_mount must define the cleanup function the on_unmount script invokes"
    )


def test_toc_instance_keys_are_unique_per_render() -> None:
    """Each ``table_of_content`` render must mint a fresh per-instance key pair.

    Shared (global) keys would let one page's ``on_unmount`` invoke another
    page's cleanup (or short-circuit its init) under React's interleaved
    mount/unmount ordering during SPA navigation. Per-instance keys keep each
    page's watcher / observer / listeners isolated.
    """

    def _init_key_for(toc_data: list[dict[str, object]]) -> str:
        toc: Any = table_of_content("docs/test", toc_data)
        mount = _scrollspy_event_script(toc, "on_mount")
        key = re.search(r"__tocInit_\w+", mount)
        assert key is not None
        return key.group(0)

    keys = [_init_key_for([{"text": "A", "id": "a", "level": 1}]) for _ in range(3)]
    assert len(set(keys)) == len(keys), (
        f"per-render init keys must be unique, got duplicates in {keys}"
    )


def test_scrollspy_runtime_single_pushstate_per_click_after_mutation() -> None:
    """Run the *real* rendered on_mount/on_unmount scripts in jsdom and assert
    that a TOC link/heading click produces exactly one ``history.pushState``
    even after an unrelated DOM mutation (the production trigger: Prism
    highlight, copy-button icon swap, tooltip portals).

    Preconditions: Node.js and the JS deps installed in
    ``tests/toc_scrollspy_repro/node_modules`` (run ``npm ci`` in that
    directory). The test is skipped, not failed, when the toolchain is absent.

    Under the bug, the still-connected watcher re-runs ``initScrollspy()`` on
    the mutation, stacking a second listener set -> each click issues two
    identical ``pushState`` calls -> the browser Back button needs two presses.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to run the scrollspy lifecycle harness")
    if not (REPRO_DIR / "node_modules").is_dir():
        pytest.skip(
            f"run `npm ci` in {REPRO_DIR} to install the jsdom lifecycle harness",
        )

    assert node is not None
    mount, unmount, init_key, cleanup_key = _rendered_scrollspy_scripts()
    payload = json.dumps(
        {
            "mount": mount,
            "unmount": unmount,
            "init_key": init_key,
            "cleanup_key": cleanup_key,
        },
    )
    js = _LIFECYCLE_HARNESS.replace("__PAYLOAD__", payload)
    result = subprocess.run(  # noqa: S603 - node path from shutil.which, JS is our own
        [node, "-e", js],
        cwd=str(REPRO_DIR),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"lifecycle harness failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert result.stderr.strip() == "", f"unexpected stderr:\n{result.stderr}"

    payload_out = json.loads(result.stdout)

    # Mount must not itself push history (no hash scroll target in this fixture).
    assert payload_out["pushStateAfterMount"] == 0, (
        f"on_mount must not pushState, got {payload_out['pushStateAfterMount']}"
    )

    # Exactly one IntersectionObserver is created at mount. The post-mount
    # mutation must NOT create a second one (that's the leak the fix prevents).
    assert payload_out["ioAfterMount"] == 1, (
        f"expected 1 IntersectionObserver at mount, got {payload_out['ioAfterMount']}"
    )
    assert payload_out["ioAfterMutation"] == 1, (
        "the post-mount DOM mutation must not create a second IntersectionObserver "
        f"(watcher re-init leak); got {payload_out['ioAfterMutation']}"
    )

    # One click on a TOC link and one on a heading anchor: exactly two
    # pushState entries total (one per click), with distinct fragments.
    clicks_to_pushstate = (
        payload_out["pushStateAfterClicks"] - payload_out["pushStateAfterMount"]
    )
    assert clicks_to_pushstate == LIFECYCLE_CLICK_COUNT, (
        "each click must push exactly one history entry (one per click); "
        f"got {clicks_to_pushstate} pushState calls for {LIFECYCLE_CLICK_COUNT} clicks — "
        "this is the back-button-needs-multiple-presses bug"
    )
    assert payload_out["pushStateUrls"] == ["#a", "#b"], (
        f"expected pushState urls [#a, #b], got {payload_out['pushStateUrls']}"
    )

    # on_unmount must disconnect the IntersectionObserver.
    assert payload_out["ioAfterUnmount"] == 1, (
        "on_unmount must disconnect the IntersectionObserver "
        f"(got {payload_out['ioAfterUnmount']} disconnects)"
    )

    # Clicks after unmount must be no-ops (listeners aborted via AbortSignal).
    post_unmount_clicks = (
        payload_out["pushStateAfterUnmountClicks"] - payload_out["pushStateAfterClicks"]
    )
    assert post_unmount_clicks == 0, (
        "clicks after on_unmount must not pushState (listeners must be removed); "
        f"got {post_unmount_clicks} extra pushState calls"
    )

    # on_unmount must clear the per-instance guards from window.
    assert payload_out["initKeyPresent"] is False, (
        "on_unmount must delete the init guard so the next mount starts clean"
    )
    assert payload_out["cleanupKeyPresent"] is False, (
        "on_unmount must delete the cleanup function so a second on_unmount is a no-op"
    )


def test_scrollspy_runtime_failure_path_watcher_disconnects_after_first_success() -> (
    None
):
    """When ``.toc-link`` is absent at mount, the watcher must start observing,
    succeed on the mutation that renders the links, and disconnect so the
    next mutation does not re-init and stack a duplicate listener set.

    Preconditions: same as the success-path runtime test.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to run the scrollspy lifecycle harness")
    if not (REPRO_DIR / "node_modules").is_dir():
        pytest.skip(
            f"run `npm ci` in {REPRO_DIR} to install the jsdom lifecycle harness",
        )

    assert node is not None
    mount, _unmount, _init_key, _cleanup_key = _rendered_scrollspy_scripts()
    payload = json.dumps({"mount": mount})
    js = _FAILURE_PATH_HARNESS.replace("__PAYLOAD__", payload)
    result = subprocess.run(  # noqa: S603 - node path from shutil.which, JS is our own
        [node, "-e", js],
        cwd=str(REPRO_DIR),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"failure-path harness failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert result.stderr.strip() == "", f"unexpected stderr:\n{result.stderr}"

    out = json.loads(result.stdout)

    # Empty body at mount: init fails, no IntersectionObserver created.
    assert out["ioAfterMount"] == 0, (
        f"init must not create an IntersectionObserver when .toc-link is absent; got {out['ioAfterMount']}"
    )
    # The mutation that renders the links: watcher fires, init succeeds, watcher
    # disconnects. Exactly one observer created.
    assert out["ioAfterFirstMutation"] == 1, (
        f"watcher must init exactly once when links appear; got {out['ioAfterFirstMutation']}"
    )
    # A second unrelated mutation must NOT re-init (watcher already disconnected).
    assert out["ioAfterSecondMutation"] == 1, (
        "after the watcher disconnects on its first success, a later mutation must "
        f"not stack a second init; got {out['ioAfterSecondMutation']}"
    )
    # One click -> exactly one pushState (listener attached exactly once).
    assert out["pushStateAfterClick"] == 1, (
        f"a single click must push exactly one history entry; got {out['pushStateAfterClick']}"
    )
    assert out["pushStateUrls"] == ["#a"], (
        f"expected pushState urls [#a], got {out['pushStateUrls']}"
    )


_LIFECYCLE_HARNESS = r"""
const { JSDOM } = require("jsdom");
const payload = __PAYLOAD__;

const dom = new JSDOM(
  '<!DOCTYPE html><html><body></body></html>',
  { url: "https://example.com/docs/getting-started/dev" }
);
const window = dom.window;
globalThis.window = window;
globalThis.document = window.document;
globalThis.navigator = window.navigator;
globalThis.history = window.history;
globalThis.location = window.location;
globalThis.MutationObserver = window.MutationObserver;
globalThis.AbortController = window.AbortController;

// jsdom does not ship IntersectionObserver; stub it to count creations/disconnects.
let ioCreated = 0;
let ioDisconnected = 0;
class IntersectionObserver {
  constructor(cb, opts) { this.cb = cb; this.opts = opts; this.targets = []; ioCreated++; }
  observe(t) { this.targets.push(t); }
  unobserve() {}
  disconnect() { ioDisconnected++; }
  takeRecords() { return []; }
}
window.IntersectionObserver = IntersectionObserver;
globalThis.IntersectionObserver = IntersectionObserver;

// jsdom does not implement scrollIntoView.
window.Element.prototype.scrollIntoView = function () {};

// Instrument history.pushState to record every url pushed.
const pushStateCalls = [];
const origPushState = window.history.pushState.bind(window.history);
window.history.pushState = function (state, title, url) {
  pushStateCalls.push(url);
  origPushState(state, title, url);
};

// A realistic TOC document: two .toc-link entries plus h1/h2 heading anchors.
document.body.innerHTML = [
  '<a class="toc-link" href="#a">A</a>',
  '<a class="toc-link" href="#b">B</a>',
  '<h1 id="a"><a href="#a">A</a></h1>',
  '<h2 id="b"><a href="#b">B</a></h2>',
].join("");

const flush = () => new Promise((r) => setTimeout(r, 50));
const click = (sel) =>
  document.querySelector(sel).dispatchEvent(
    new window.MouseEvent("click", { bubbles: true, cancelable: true })
  );

async function run() {
  // 1) Mount: synchronous init should succeed (.toc-link is present), so the
  //    domWatcher must NOT be observing (the fix's whole point).
  eval(payload.mount);
  await flush();
  const pushStateAfterMount = pushStateCalls.length;
  const ioAfterMount = ioCreated;

  // 2) An unrelated DOM mutation under document.body — the production trigger
  //    (Prism.highlightAll, copy-button icon swap, tooltip portals). Under the
  //    bug, the still-connected watcher re-runs initScrollspy() here.
  document.body.appendChild(document.createElement("span"));
  await flush();
  const ioAfterMutation = ioCreated;

  // 3) Click a TOC link and a heading anchor: each must push exactly ONE entry.
  click(".toc-link");
  click("h2 a");
  await flush();
  const pushStateAfterClicks = pushStateCalls.length;

  // 4) Unmount: the on_unmount script must abort listeners, disconnect the
  //    IntersectionObserver, disconnect the watcher, and clear the guards.
  eval(payload.unmount);
  await flush();
  const ioAfterUnmount = ioDisconnected;

  // 5) Clicks after unmount must be no-ops (listeners removed via AbortSignal).
  click(".toc-link");
  click("h2 a");
  await flush();
  const pushStateAfterUnmountClicks = pushStateCalls.length;

  console.log(JSON.stringify({
    pushStateAfterMount,
    ioAfterMount,
    ioAfterMutation,
    pushStateAfterClicks,
    ioAfterUnmount,
    pushStateAfterUnmountClicks,
    pushStateUrls: pushStateCalls,
    initKeyPresent: typeof window[payload.init_key] !== "undefined",
    cleanupKeyPresent: typeof window[payload.cleanup_key] !== "undefined",
  }));
}

run().catch((e) => { console.error(e); process.exit(1); });
"""


_FAILURE_PATH_HARNESS = r"""
const { JSDOM } = require("jsdom");
const payload = __PAYLOAD__;

const dom = new JSDOM(
  '<!DOCTYPE html><html><body></body></html>',
  { url: "https://example.com/docs/getting-started/dev" }
);
const window = dom.window;
globalThis.window = window;
globalThis.document = window.document;
globalThis.navigator = window.navigator;
globalThis.history = window.history;
globalThis.location = window.location;
globalThis.MutationObserver = window.MutationObserver;
globalThis.AbortController = window.AbortController;

let ioCreated = 0;
class IntersectionObserver {
  constructor(cb, opts) { this.cb = cb; this.opts = opts; this.targets = []; ioCreated++; }
  observe(t) { this.targets.push(t); }
  unobserve() {}
  disconnect() {}
  takeRecords() { return []; }
}
window.IntersectionObserver = IntersectionObserver;
globalThis.IntersectionObserver = IntersectionObserver;
window.Element.prototype.scrollIntoView = function () {};

const pushStateCalls = [];
const origPushState = window.history.pushState.bind(window.history);
window.history.pushState = function (state, title, url) {
  pushStateCalls.push(url);
  origPushState(state, title, url);
};

// Empty body: .toc-link is absent, so the synchronous init at mount must fail
// and the watcher must start observing.
document.body.innerHTML = "";

const flush = () => new Promise((r) => setTimeout(r, 50));

async function run() {
  eval(payload.mount);
  await flush();
  const ioAfterMount = ioCreated;

  // Render the TOC links + sections after mount — the mutation that lets the
  // watcher's deferred init succeed.
  document.body.innerHTML =
    '<a class="toc-link" href="#a">A</a><h1 id="a"><a href="#a">A</a></h1>';
  await flush();
  const ioAfterFirstMutation = ioCreated;

  // A second, unrelated mutation: the watcher must already have disconnected on
  // its first success, so this must NOT re-init.
  document.body.appendChild(document.createElement("span"));
  await flush();
  const ioAfterSecondMutation = ioCreated;

  document.querySelector(".toc-link").dispatchEvent(
    new window.MouseEvent("click", { bubbles: true, cancelable: true })
  );
  await flush();
  const pushStateAfterClick = pushStateCalls.length;

  console.log(JSON.stringify({
    ioAfterMount,
    ioAfterFirstMutation,
    ioAfterSecondMutation,
    pushStateAfterClick,
    pushStateUrls: pushStateCalls,
  }));
}

run().catch((e) => { console.error(e); process.exit(1); });
"""
