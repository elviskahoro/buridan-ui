# ruff: noqa: INP001  # tests/ is an implicit namespace package like every other test file in this repo.
"""Regression coverage for the autocomplete Escape-to-close animation bug.

The autocomplete popup runs a 100ms fade-out animation: ``closePopup`` defers
``setOpen(false)`` and ``setHighlighted(-1)`` to a ``setTimeout`` so the popup
can animate out, while ``closing`` flips on synchronously. The popup's keyboard
handler ``handleKeyDown`` used to guard only on ``open`` — which stays ``true``
for the entire 100ms close window — so Enter and the Arrow keys kept acting on
the animating-out popup: a fast Escape→Enter committed the item the user just
dismissed (if one was already highlighted), and Escape→Arrow→Enter committed a
*different*, hidden item.

The fix keys the guard off ``closing`` as well: ``if (!open || closing) return;``.
Because ``closePopup`` sets ``closing`` synchronously, the moment Escape is
pressed no further keydown is processed until the popup reopens.

Coverage is layered so CI (which has no Node toolchain) still catches the
regression, and a tooled environment verifies the behavior end-to-end:

1. Static source-shape assertions on the embedded ``BURIDAN_AUTOCOMPLETE_JS``
   string (always run, no JS toolchain) — they encode the invariants the fix
   depends on: the guard checks ``closing`` (the fix), ``closePopup`` sets
   ``closing`` synchronously before the timer (so the guard is armed the
   instant Escape is pressed), and ``openPopup`` clears ``closing`` before
   re-enabling the popup (so keys work again after a close/reopen cycle).
2. A jsdom + react-dom runtime harness that mounts the *real*
   ``BuridanAutocompleteRoot`` (JSX transpiled with esbuild) and drives the
   Escape→Enter and Escape→Arrow→Enter sequences that expose the bug. Under
   the pre-fix guard, ``onSelectItem`` fires for an item the user just
   dismissed. The harness is skipped (not failed) when the JS toolchain is
   absent, mirroring the ``tests/test_toc_scrollspy.py`` precedent.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from components.ui.autocomplete import BURIDAN_AUTOCOMPLETE_JS

REPRO_DIR = Path(__file__).parent / "autocomplete_repro"


def _component_js() -> str:
    """Return the embedded ``BURIDAN_AUTOCOMPLETE_JS`` string as-shipped."""
    return BURIDAN_AUTOCOMPLETE_JS


def _extract_function(name: str) -> str:
    """Brace-match a ``function name(...) { ... }`` declaration out of the
    embedded JS string. Stays valid even when the body grows inner brace blocks
    and when the parameter list itself contains braces (e.g. a destructured
    object parameter like ``BuridanAutocompleteRoot({ items = [], ... })``).

    The function body opens at the first ``{`` *after* the parameter list's
    closing ``)`` (matched paren-deep from the ``function name(`` opening), so
    a destructuring ``{...}`` in the parameter list is not mistaken for the
    body and truncation does not occur.
    """
    source = _component_js()
    start = source.index(f"function {name}(")
    paren_open = source.index("(", start)
    paren_depth = 0
    paren_close = -1
    for idx in range(paren_open, len(source)):
        char = source[idx]
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
            if paren_depth == 0:
                paren_close = idx
                break
    if paren_close == -1:
        msg = f"unterminated parameter list in function {name}"
        raise AssertionError(msg)
    open_brace = source.index("{", paren_close)
    depth = 0
    for idx in range(open_brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]
    msg = f"unterminated function {name} in BURIDAN_AUTOCOMPLETE_JS"
    raise AssertionError(msg)


def _handle_keydown_source() -> str:
    return _extract_function("handleKeyDown")


def _close_popup_source() -> str:
    return _extract_function("closePopup")


def _open_popup_source() -> str:
    return _extract_function("openPopup")


def _buridan_autocomplete_root_source() -> str:
    """Return ``BuridanAutocompleteRoot`` plus its sibling top-level helper
    ``injectScrollLockStyle`` (called from the component's mount effect).

    Both functions are concatenated so the runtime harness transpiles and
    evaluates them in a single ``new Function`` scope — without
    ``injectScrollLockStyle`` in scope the component's mount effect throws a
    ``ReferenceError`` and the render aborts before any input exists.
    """
    return (
        _extract_function("injectScrollLockStyle")
        + "\n"
        + _extract_function("BuridanAutocompleteRoot")
    )


# ─── STATIC SOURCE-SHAPE GUARANTEES ────────────────────────────────────────


def test_handlekeydown_guard_blocks_keys_while_closing() -> None:
    """``handleKeyDown`` must short-circuit while ``closing`` is true.

    ``closePopup`` defers ``setOpen(false)`` to a 100ms ``setTimeout``, so the
    ``open`` flag stays ``true`` throughout the close-animation window. The guard
    must therefore also check ``closing`` (which ``closePopup`` flips on
    synchronously) or Enter/Arrow keys remain active against the animating-out
    popup — a fast Escape→Enter commits the item the user just dismissed.
    """
    src = _handle_keydown_source()

    assert re.search(
        r"if\s*\(\s*!open\s*\|\|\s*closing\s*\)\s*return\s*;",
        src,
    ), (
        "handleKeyDown must guard on `closing` as well as `open` to ignore keys "
        "during the 100ms close animation."
    )


def test_closepopup_sets_closing_synchronously_before_timer() -> None:
    """``closePopup`` must flip ``closing`` on synchronously (before the
    ``setTimeout``) so the keydown guard fires the instant Escape is pressed —
    not 100ms later when the timer finally resets ``open``.
    """
    src = _close_popup_source()

    assert "setClosing(true)" in src
    assert "setTimeout" in src
    assert src.index("setClosing(true)") < src.index("setTimeout"), (
        "closePopup must call setClosing(true) before starting the setTimeout "
        "so the keydown guard is armed immediately on Escape."
    )


def test_openpopup_clears_closing_and_pending_timer_synchronously() -> None:
    """Reopening must re-arm key handling: ``openPopup`` cancels any pending
    close timer and clears ``closing`` synchronously, before re-enabling the
    popup — so the guard no longer short-circuits once the popup is usable.
    """
    src = _open_popup_source()

    assert "clearTimeout" in src
    assert "setClosing(false)" in src

    closing_idx = src.index("setClosing(false)")
    open_idx = src.index("setOpen(true)")
    assert closing_idx < open_idx, (
        "openPopup must clear `closing` before re-enabling the popup, or the "
        "keydown guard would ignore keys on a popup the user just reopened."
    )


# ─── RUNTIME HARNESS ──────────────────────────────────────────────────────


def _runtime_toolchain() -> tuple[str | None, str]:
    """Return ``(node_path, skip_reason)``. A non-empty reason means skip."""
    node = shutil.which("node")
    if not node:
        return None, "Node.js is required to run the autocomplete runtime harness"
    if not (REPRO_DIR / "node_modules").is_dir():
        return (
            node,
            f"run `npm ci` in {REPRO_DIR} to install the esbuild+jsdom+react harness",
        )
    return node, ""


def test_autocomplete_ignores_keys_during_close_animation() -> None:
    """Mount the real ``BuridanAutocompleteRoot`` and drive the Escape→Enter and
    Escape→Arrow→Enter sequences that expose the bug.

    Preconditions: Node.js and the JS deps installed in
    ``tests/autocomplete_repro/node_modules`` (run ``npm ci`` in that
    directory). The test is skipped, not failed, when the toolchain is absent.

    Behavioral guarantees verified:

    - Escape→Enter *within* the 100ms close window does NOT commit
      ``onSelectItem`` and does NOT rewrite the input value (the bug case).
    - Escape→Arrow→Enter within the window does NOT commit a (different, hidden)
      item.
    - Enter on an open popup (no Escape) still commits the highlighted item —
      the fix does not break the normal select path.
    - Enter *after* the close timer fired is still ignored (``open`` is then
      false) — no regression in the post-close behavior.
    - After the popup reopens, a subsequent Enter commits the item — the fix
      does not break the reopen path.
    """
    node, reason = _runtime_toolchain()
    if reason:
        pytest.skip(reason)

    assert node is not None
    js = _RUNTIME_HARNESS.replace(
        "__BURIDAN_AUTOCOMPLETE_ROOT_SRC__",
        json.dumps(_buridan_autocomplete_root_source()),
    )
    result = subprocess.run(  # noqa: S603  # node + js are test-controlled, not untrusted input
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

    # Bug case A: Escape then Enter WITHIN the close window.
    case_a = payload["escape_then_enter"]
    assert case_a["selected"] == [], (
        "Escape→Enter within the close window must not fire onSelectItem; "
        f"got {case_a['selected']!r}"
    )
    assert case_a["inputValue"] == "a", (
        "Escape→Enter within the close window must not rewrite the input; "
        f"got {case_a['inputValue']!r}"
    )
    assert case_a["popupMountedAtEnterTime"] is True, (
        "the popup must still be mounted during the close window (proves the "
        "test hit the closing state); a False here means handleSelect already "
        "fired and unmounted the popup — the bug."
    )

    # Bug case B: Escape then Arrow then Enter within the close window.
    case_b = payload["escape_arrow_then_enter"]
    assert case_b["selected"] == [], (
        "Escape→Arrow→Enter within the close window must not fire onSelectItem; "
        f"got {case_b['selected']!r}"
    )
    assert case_b["inputValue"] == "a", (
        "Escape→Arrow→Enter within the close window must not rewrite the "
        f"input; got {case_b['inputValue']!r}"
    )

    # Control C: Enter on an open popup commits the highlighted item.
    case_c = payload["enter_no_escape"]
    assert case_c["selected"] == ["alpha"], (
        "Enter on an open popup must still commit the highlighted item; "
        f"got {case_c['selected']!r}"
    )
    assert case_c["inputValue"] == "alpha", (
        f"Enter on an open popup must rewrite the input to the selected label; "
        f"got {case_c['inputValue']!r}"
    )

    # Control D: Enter after the close timer fired is still ignored.
    case_d = payload["enter_after_close"]
    assert case_d["selected"] == [], (
        "Enter after the close timer fired must be ignored (open is false); "
        f"got {case_d['selected']!r}"
    )

    # Control E: after the popup reopens, Enter commits the item.
    case_e = payload["reopen_then_enter"]
    assert case_e["selected"] == ["alpha"], (
        "After the popup reopens, Enter must commit the highlighted item; "
        f"got {case_e['selected']!r}"
    )


_RUNTIME_HARNESS = r"""
const esbuild = require("esbuild");
const { JSDOM } = require("jsdom");

// The real BuridanAutocompleteRoot source (JSX, plus the sibling
// injectScrollLockStyle helper), extracted verbatim from
// components/ui/autocomplete.py and injected by the Python test as a JSON
// string literal so esbuild can transpile the JSX.
const COMP_SRC = __BURIDAN_AUTOCOMPLETE_ROOT_SRC__;

// Set up the jsdom globals BEFORE requiring react-dom: react-dom's event
// system attaches to `document`/`window` at require time, and if those are
// unset (plain Node has no DOM) the input-event change polyfill later fails
// with 'Cannot read properties of null (reading tag)' in
// getTargetInstForInputEventPolyfill because the input node's fiber is not
// found in the (wrong-document) instance map.
const dom = new JSDOM(
  '<!DOCTYPE html><html><head></head><body><div id="root"></div></body></html>',
  { url: "https://example.com/" }
);
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.navigator = dom.window.navigator;
// act() must run in the React act environment so synchronous state updates
// inside event handlers are flushed before assertions.
globalThis.IS_REACT_ACT_ENVIRONMENT = true;

const React = require("react");
const ReactDOM = require("react-dom");
const { createRoot } = require("react-dom/client");
const { act } = require("react");

// Transpile the JSX function to plain JS. esbuild's transformSync is
// synchronous and needs no bundler; the classic JSX runtime emits
// React.createElement calls, matching the React in scope below.
const transpiled = esbuild.transformSync(COMP_SRC, {
  loader: "jsx",
  jsx: "transform",
}).code;

// Evaluate the function declarations in a scope that provides React / ReactDOM
// (the embedded source uses both React.useState etc. and ReactDOM.createPortal).
const factory = new Function(
  "React",
  "ReactDOM",
  transpiled + "\n; return BuridanAutocompleteRoot;"
);
const BuridanAutocompleteRoot = factory(React, ReactDOM);

const selected = [];

const root = createRoot(document.getElementById("root"));
act(() => {
  root.render(
    React.createElement(BuridanAutocompleteRoot, {
      items: ["alpha", "beta", "gamma"],
      placeholder: "Search",
      onSelectItem: (v) => { selected.push(v); },
      onChangeQuery: () => {},
      setQueryOnSelect: true,
      rootClass: "root",
      inputClass: "input",
      popupClass: "popup",
      listClass: "list",
      itemClass: "item",
      itemHighlightedClass: "hl",
      emptyClass: "empty",
      groupLabelClass: "gl",
      separatorClass: "sep",
    })
  );
});

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

function setType(element, value) {
  const setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, "value"
  ).set;
  setter.call(element, value);
  element.dispatchEvent(new window.Event("input", { bubbles: true }));
}

function keydown(element, k) {
  element.dispatchEvent(
    new window.KeyboardEvent("keydown", {
      key: k,
      bubbles: true,
      cancelable: true,
    })
  );
}

// Wrap a synchronous interaction in act so React flushes the state update and
// re-renders before the next interaction or assertion reads it.
async function interact(fn) { await act(fn); }

// Wait real time for a pending setTimeout (the close animation's 100ms timer)
// to fire, wrapped in act so the timer's setState calls are flushed.
async function wait(ms) { await act(async () => { await sleep(ms); }); }

async function resetInput(input) {
  await interact(() => setType(input, ""));
  await interact(() => setType(input, "a"));
}

async function run() {
  const input = document.querySelector("input");
  if (!input) throw new Error("input not rendered");

  const out = {};

  // ── Case A: Escape then Enter WITHIN the close window (the bug) ──
  selected.length = 0;
  await resetInput(input); // popup open with the full list
  await interact(() => keydown(input, "ArrowDown")); // highlight alpha (idx 0)
  await interact(() => keydown(input, "Escape"));
  await wait(30); // inside the 100ms closing window — closing=true, open=true
  // The popup must still be mounted at enter time: this proves the test
  // genuinely hit the closing window (a False here would mean the popup
  // already unmounted, i.e. the bug didn't reproduce).
  const popupMountedAtEnter = document.querySelector(".popup") !== null;
  await interact(() => keydown(input, "Enter")); // must be ignored (closing)
  out.escape_then_enter = {
    selected: [...selected],
    inputValue: input.value,
    popupMountedAtEnterTime: popupMountedAtEnter,
  };
  await wait(150); // let the close timer fire + reset before the next case

  // ── Case B: Escape then Arrow then Enter within the window (hidden highlight) ──
  selected.length = 0;
  await resetInput(input);
  await interact(() => keydown(input, "ArrowDown")); // highlight alpha (idx 0)
  await interact(() => keydown(input, "Escape"));
  await wait(30);
  await interact(() => keydown(input, "ArrowDown")); // must be ignored (closing)
  await interact(() => keydown(input, "Enter")); // must NOT commit a hidden item
  out.escape_arrow_then_enter = {
    selected: [...selected],
    inputValue: input.value,
  };
  await wait(150);

  // ── Case C: Enter on an open popup commits the highlighted item (no regression) ──
  selected.length = 0;
  await resetInput(input);
  await interact(() => keydown(input, "ArrowDown")); // highlight alpha
  await interact(() => keydown(input, "Enter")); // commit alpha (no Escape first)
  out.enter_no_escape = {
    selected: [...selected],
    inputValue: input.value,
  };

  // ── Case D: Enter AFTER the close timer fired is still ignored ──
  selected.length = 0;
  await resetInput(input);
  await interact(() => keydown(input, "ArrowDown")); // highlight alpha
  await interact(() => keydown(input, "Escape"));
  await wait(150); // past the close window — timer fired, open=false
  await interact(() => keydown(input, "Enter")); // open is now false -> ignored
  out.enter_after_close = {
    selected: [...selected],
    inputValue: input.value,
  };

  // ── Case E: after the popup reopens, Enter commits the item ──
  selected.length = 0;
  await resetInput(input); // reopen the popup
  await interact(() => keydown(input, "ArrowDown")); // highlight alpha
  await interact(() => keydown(input, "Enter")); // commit alpha
  out.reopen_then_enter = {
    selected: [...selected],
    inputValue: input.value,
  };

  console.log(JSON.stringify(out));
}

run().catch((err) => {
  console.error("HARNESS_ERROR:", err && err.stack ? err.stack : err);
  process.exit(1);
});
"""
