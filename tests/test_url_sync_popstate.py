"""Regression coverage for the popstate handler in ``app/engine/url_sync.py``.

Background: commit cf1a044 ("engine: offload reflex logic to client side")
deleted ``theme = ClientStateVar.create("theme", {})`` (which had registered
``window.refs['_client_state_setTheme']``) and rewrote ``app/engine/actions.py``
to apply themes directly to the DOM, but left the popstate handler in
``url_sync_engine()`` calling the now-unregistered setter ref. Every Back /
Forward navigation on ``/create`` therefore threw
``TypeError: window.refs._client_state_setTheme is not a function`` and aborted
before restoring the seed or syncing the sidebar — leaving the UI and the URL-
derived seed out of sync (the stale seed then corrupted later history entries).

These tests pin the migrated, client-side-direct-DOM pattern that the actions
already use, and guard against both the original crashing call and the dead
``window._generateFromSeed`` (single-underscore) fallback returning.
"""

import json
import re
import shutil
import subprocess

import pytest

from app.engine.url_sync import url_sync_engine


def _url_sync_js() -> str:
    """Extract the raw JS emitted by ``url_sync_engine()``.

    Mirrors the extraction path used by ``tests/test_seed_codec.py`` for
    ``seed_engine()``: the ``rx.script`` wraps a single ``Bare`` child whose
    ``contents`` Var holds the script source.
    """
    return url_sync_engine().children[0].children[0].contents._var_value


def _popstate_block(js: str) -> str:
    """Return the body of the ``addEventListener('popstate', ...)`` handler."""
    match = re.search(
        r"addEventListener\(\s*['\"]popstate['\"]\s*,\s*\(event\)\s*=>\s*\{(.*)\}\s*\);?\s*\Z",
        js,
        re.DOTALL,
    )
    assert match is not None, "popstate handler not found in url_sync_engine() output"
    return match.group(1)


# ---------------------------------------------------------------------------
# Static guarantees (no Node.js required) — the regression guards
# ---------------------------------------------------------------------------


def test_url_sync_no_longer_calls_removed_set_theme_ref() -> None:
    """The popstate handler must not call ``refs['_client_state_setTheme']``.

    The ``theme`` ClientStateVar was removed in cf1a044 and no component
    registers ``_client_state_setTheme`` anymore, so any call to it throws a
    ``TypeError`` that aborts the entire Back/Forward restore. This is the
    exact key with the closing quote immediately after ``setTheme`` — it must
    not be confused with the legitimate ``_client_state_setTheme_color`` key
    used by ``__syncSidebar``.
    """
    js = _url_sync_js()
    assert not re.search(r"refs\[\s*['\"]_client_state_setTheme['\"]\s*\]", js), (
        "popstate handler must not call the removed refs['_client_state_setTheme']"
    )


def test_url_sync_dead_single_underscore_fallback_is_removed() -> None:
    """The dead ``window._generateFromSeed`` fallback must be gone.

    Only ``window.__generateFromSeed`` (double underscore, defined in
    ``app/engine/seed.py``) exists in the codebase; ``window._generateFromSeed``
    (single underscore) was defined nowhere, so the fallback branch was
    unreachable dead code that could never rescue the handler. The pattern is
    anchored on the dot before a *single* underscore so it does not match the
    legitimate ``window.__generateFromSeed``.
    """
    js = _url_sync_js()
    assert not re.search(r"window\._generateFromSeed\b", js), (
        "dead window._generateFromSeed (single underscore) fallback must be removed"
    )
    # The legitimate double-underscore global must still be used.
    assert "window.__generateFromSeed" in js


def test_url_sync_defines_apply_theme_to_dom_helper() -> None:
    """The handler must apply themes directly to the DOM, like the actions.

    ``app/engine/actions.py`` was migrated in cf1a044 to a direct-DOM pattern
    via an inlined ``_applyToRoot`` helper. The popstate handler must expose an
    equivalent helper so it does not depend on the removed setter ref.
    """
    js = _url_sync_js()
    assert re.search(r"window\.__applyThemeToDOM\s*=\s*function", js), (
        "popstate handler must define window.__applyThemeToDOM"
    )


def test_url_sync_apply_theme_to_dom_targets_preview_container_and_filters_css_vars() -> (
    None
):
    """``__applyThemeToDOM`` must mirror the actions' ``_applyToRoot``.

    It must target ``#theme-preview-container`` (falling back to the document
    element) so site styles are unaffected, and it must only write keys that
    start with ``--`` (the CSS custom properties), exactly like
    ``_applyToRoot`` in ``app/engine/actions.py``.
    """
    js = _url_sync_js()
    assert "getElementById('theme-preview-container')" in js
    assert "document.documentElement" in js
    assert "k.startsWith('--')" in js


def test_url_sync_popstate_guards_ref_access_like_actions() -> None:
    """Every ``refs[...]`` setter call inside the handler must be guarded.

    The actions were hardened in cf1a044 to guard each ref access with
    ``if (refs['...'])``. The popstate handler must follow the same pattern so
    a missing ref never aborts the whole restore again. In particular,
    ``setSeed`` must be guarded (the unguarded ``setTheme`` call was the bug).
    """
    popstate_block = _popstate_block(_url_sync_js())
    assert re.search(
        r"if\s*\(\s*window\.refs\[\s*['\"]_client_state_setSeed['\"]\s*\]\s*\)\s*"
        r"window\.refs\[\s*['\"]_client_state_setSeed['\"]\s*\]\s*\(",
        popstate_block,
    ), "setSeed must be guarded with if (window.refs['_client_state_setSeed'])"


def test_url_sync_popstate_guards_sync_sidebar_and_generate_from_seed() -> None:
    """``__syncSidebar`` and the seed-derivation must be guarded too.

    The handler must not assume ``window.__syncSidebar`` or
    ``window.__generateFromSeed`` are present; both must be checked before
    use, mirroring the ``if (window.__syncSidebar)``/``window.__updatePresetURL``
    guards used throughout the actions.
    """
    popstate_block = _popstate_block(_url_sync_js())
    assert "if (window.__syncSidebar)" in popstate_block
    assert "__generateFromSeed" in popstate_block
    assert "!window.__generateFromSeed" in popstate_block


def test_url_sync_popstate_restores_seed_input_value() -> None:
    """The handler must keep the on-page seed input in sync with the restore.

    On Back/Forward, the visible seed input (``#seed-input-el``) would otherwise
    keep showing the stale seed. The actions' ``SHUFFLE``/``INITIAL_LOAD``
    helpers set ``el.value = s`` after changing the seed; the popstate handler
    must do the same so the input matches the restored URL/seed.
    """
    popstate_block = _popstate_block(_url_sync_js())
    assert "getElementById('seed-input-el')" in popstate_block
    assert re.search(r"el\.value\s*=\s*seed", popstate_block)


def test_url_sync_apply_theme_to_dom_matches_actions_apply_to_root_logic() -> None:
    """The two apply-to-DOM helpers must stay in lockstep.

    ``url_sync.__applyThemeToDOM`` and the actions' inlined ``_applyToRoot``
    must target the same element (``#theme-preview-container`` with
    ``documentElement`` fallback) and use the same ``--`` key filter, so the
    popstate restore paints exactly the same theme an action would. This guard
    prevents the two implementations from silently diverging again (which is
    what happened to the popstate handler in cf1a044).
    """
    from app.engine.actions import _engine_js

    actions_block_match = re.search(
        r"function _applyToRoot\(config\)\s*\{(.*?)\}",
        _engine_js(),
        re.DOTALL,
    )
    assert actions_block_match is not None, "_applyToRoot not found in actions engine"
    actions_block = actions_block_match.group(1)

    url_block_match = re.search(
        r"window\.__applyThemeToDOM\s*=\s*function\(config\)\s*\{(.*?)\};",
        _url_sync_js(),
        re.DOTALL,
    )
    assert url_block_match is not None, "__applyThemeToDOM not found in url_sync engine"
    url_block = url_block_match.group(1)

    for fragment in (
        "getElementById('theme-preview-container')",
        "document.documentElement",
        "k.startsWith('--')",
        "setProperty(k, v)",
    ):
        assert fragment in actions_block, f"_applyToRoot lost fragment: {fragment}"
        assert fragment in url_block, (
            f"__applyThemeToDOM diverged from _applyToRoot on: {fragment}"
        )


# ---------------------------------------------------------------------------
# End-to-end JS execution (requires Node.js; skipped if unavailable)
#
# Mirrors the convention in tests/test_seed_codec.py: guard with
# shutil.which("node") and pytest.skip when Node is not on PATH. The CI
# runner (ubuntu-latest, .github/workflows/tests.yml) has Node installed.
# ---------------------------------------------------------------------------


def _run_popstate(setup_js: str, dispatch_js: str, output_js: str) -> dict[str, object]:
    """Execute ``url_sync_engine()`` against a mock and dispatch one popstate.

    Structure: ``setup_js`` builds the pre-``url_sync`` mock (window.refs,
    document, location, spies, and any ``window.__generateFromSeed``); then
    the real ``url_sync`` JS runs (registering helpers + the popstate
    listener); then spies wrap the url_sync-defined ``__applyThemeToDOM`` and
    ``__syncSidebar`` so calls are recorded while ``__applyThemeToDOM`` still
    mutates the mock DOM; then ``dispatch_js`` invokes the captured handler;
    then ``output_js`` prints a JSON summary on stdout.

    The mock DOM provides a ``style`` object whose ``setProperty`` records
    onto the object (the real ``CSSStyleDeclaration.setProperty`` would),
    and a ``document.documentElement`` fallback with the same kind of style,
    so the ``__applyThemeToDOM`` helper (which falls back to
    ``document.documentElement`` when ``#theme-preview-container`` is absent)
    never crashes on `target.style.setProperty is not a function`.
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the popstate handler")

    base_setup = r"""
    const window = globalThis;
    const calls = { setSeed: [], syncSidebar: [], applyDom: [] };

    function makeStyle() {
        const s = {};
        s.setProperty = function(k, v) { s[k] = v; };
        return s;
    }

    const themeContainer = { style: makeStyle() };
    const seedInput = { value: '' };

    window.document = {
        getElementById: function(id) {
            if (id === 'theme-preview-container') return themeContainer;
            if (id === 'seed-input-el') return seedInput;
            return null;
        },
        documentElement: { style: makeStyle() }
    };

    let popstateHandler = null;
    window.addEventListener = function(type, handler) {
        if (type === 'popstate') popstateHandler = handler;
    };

    window.history = { pushState: function() {}, replaceState: function() {} };
    """
    spy_wrap = r"""
    if (popstateHandler === null) throw new Error('popstate handler was never registered');

    // Wrap url_sync's __applyThemeToDOM so each call is recorded while the
    // real implementation still mutates the mock DOM.
    const _origApply = window.__applyThemeToDOM;
    window.__applyThemeToDOM = function(config) {
        calls.applyDom.push(config);
        if (_origApply) return _origApply(config);
    };

    // url_sync's own __syncSidebar needs window.__BASE_THEMES etc., which the
    // popstate test does not mount; replace it with a pure spy so the handler's
    // "did it call __syncSidebar?" contract is observed regardless.
    window.__syncSidebar = function(config) { calls.syncSidebar.push(config); };
    """
    js = (
        "const globalThis = this;\n"
        + base_setup
        + setup_js
        + _url_sync_js()
        + spy_wrap
        + dispatch_js
        + output_js
    )
    result = subprocess.run(
        [node, "-e", js],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def test_popstate_handler_restores_theme_without_crashing_post_cf1a044() -> None:
    """End-to-end: Back/Forward must restore theme, seed, input, and sidebar.

    Reproduces the post-cf1a044 runtime (refs populated but
    ``_client_state_setTheme`` absent). Before the fix, dispatching popstate
    with ``{preset: 'b0'}`` threw ``TypeError: ... is not a function`` and
    skipped ``setSeed`` and ``__syncSidebar``. After the fix, the handler must
    apply CSS vars directly to ``#theme-preview-container``, call ``setSeed``,
    update ``#seed-input-el``, and call ``__syncSidebar`` — with no exception.
    """
    setup = r"""
    window.refs = {
        _client_state_darkmode: false,
        _client_state_setSeed: function(s) { calls.setSeed.push(s); },
        // NOTE: _client_state_setTheme intentionally absent — cf1a044 removed it.
    };
    window.location = { search: '', href: 'http://localhost/create' };
    window.__generateFromSeed = function(seed, dark) {
        return {
            '--background': 'oklch(1 0 0)',
            '--primary': 'oklch(0.205 0 0)',
            '__base_id': 'neutral',
            '__seed': seed,
            '__dark': dark
        };
    };
    """
    dispatch = r"""
    const errors = [];
    try { popstateHandler({ state: { preset: 'b0' } }); }
    catch (e) { errors.push(String(e)); }
    """
    output = r"""
    console.log(JSON.stringify({
        errors: errors,
        setSeed: calls.setSeed,
        syncSidebarCount: calls.syncSidebar.length,
        applyDomCount: calls.applyDom.length,
        backgroundVar: themeContainer.style['--background'],
        primaryVar: themeContainer.style['--primary'],
        seedInputValue: seedInput.value
    }));
    """
    payload = _run_popstate(setup, dispatch, output)

    # The original bug: an uncaught TypeError aborted the handler. No more.
    assert payload["errors"] == [], f"popstate handler threw: {payload['errors']}"

    # Theme was applied directly to the DOM via __applyThemeToDOM.
    assert payload["applyDomCount"] == 1
    assert payload["backgroundVar"] == "oklch(1 0 0)"
    assert payload["primaryVar"] == "oklch(0.205 0 0)"

    # Seed state and visible input were both restored from the history entry.
    assert payload["setSeed"] == ["b0"]
    assert payload["seedInputValue"] == "b0"

    # Sidebar was resynced with the restored config.
    assert payload["syncSidebarCount"] == 1


def test_popstate_handler_works_when_set_seed_ref_is_absent() -> None:
    """A missing ``_client_state_setSeed`` ref must not abort the restore.

    The actions harden ref access with ``if (refs['...'])``; the popstate
    handler follows the same pattern, so a page variant that lacks the seed
    ref still restores the theme DOM and sidebar without crashing.
    """
    setup = r"""
    window.refs = {
        _client_state_darkmode: false,
        // _client_state_setSeed intentionally absent on this page variant.
    };
    window.location = { search: '', href: 'http://localhost/' };
    window.__generateFromSeed = function(seed) {
        return { '--background': 'oklch(1 0 0)', '--primary': 'oklch(0.3 0 0)', '__seed': seed };
    };
    """
    dispatch = r"""
    let threw = false;
    try { popstateHandler({ state: { preset: 'b0' } }); }
    catch (e) { threw = true; }
    """
    output = r"""
    console.log(JSON.stringify({
        threw: threw,
        setSeed: calls.setSeed,
        applyDomCount: calls.applyDom.length,
        syncSidebarCount: calls.syncSidebar.length,
        backgroundVar: themeContainer.style['--background'],
        primaryVar: themeContainer.style['--primary']
    }));
    """
    payload = _run_popstate(setup, dispatch, output)
    assert payload["threw"] is False
    # Theme DOM and sidebar still restored even without the setSeed ref.
    assert payload["applyDomCount"] == 1
    assert payload["syncSidebarCount"] == 1
    assert payload["backgroundVar"] == "oklch(1 0 0)"
    assert payload["primaryVar"] == "oklch(0.3 0 0)"
    # No setSeed ref → handler must not have tried to call undefined.
    assert payload["setSeed"] == []
