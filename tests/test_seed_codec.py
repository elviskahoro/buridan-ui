"""Regression coverage for the packed theme preset seed format."""

import json
import os
import shutil
import subprocess
import tempfile

import pytest
import reflex as rx

from app.engine.actions import APPLY_BASE_PRIMARY_JS, INITIAL_LOAD_JS, _engine_js
from app.engine.seed import seed_engine
from app.engine.url_sync import url_sync_engine
from app.registry.colors import COLOR_THEMES
from app.registry.fonts import FONT_REGISTRY
from app.registry.radii import RADIUS_OPTIONS
from app.registry.styles import STYLE_REGISTRY
from app.registry.themes import BASE_THEMES
from cli.main import CHARS, SEED_SPACE_SIZE, decode_seed


def _to_base62(value: int, width: int) -> str:
    """Encode an integer using the seed codec's fixed-width base-62 alphabet."""
    result = ""
    for _ in range(width):
        result += CHARS[value % 62]
        value //= 62
    return result


def _seed_for_number(number: int) -> str:
    checksum = (number * 12345) % 916132832
    return _to_base62(number, 4) + _to_base62(checksum, 5)


def _packed_number(
    base_index: int,
    color_index: int,
    chart_index: int,
    style_index: int,
    font_index: int,
    radius_index: int,
) -> int:
    color_radix = len(COLOR_THEMES) + 1
    value = base_index * color_radix + color_index
    value = value * color_radix + chart_index
    value = value * len(STYLE_REGISTRY) + style_index
    value = value * len(FONT_REGISTRY) + font_index
    return value * len(RADIUS_OPTIONS) + radius_index


@pytest.mark.parametrize("font_index", range(len(FONT_REGISTRY)))
@pytest.mark.parametrize("style_index", range(len(STYLE_REGISTRY)))
@pytest.mark.parametrize("radius_index", range(len(RADIUS_OPTIONS)))
def test_cli_seed_decodes_every_font_style_and_radius(
    font_index: int, style_index: int, radius_index: int
) -> None:
    number = _packed_number(0, 0, 0, style_index, font_index, radius_index)

    assert decode_seed(_seed_for_number(number)) == {
        "baseId": BASE_THEMES[0]["id"],
        "colorId": None,
        "chartId": None,
        "styleId": STYLE_REGISTRY[style_index]["id"],
        "fontId": FONT_REGISTRY[font_index]["id"],
        "radius": RADIUS_OPTIONS[radius_index][1],
    }


def test_cli_seed_accepts_highest_valid_number_and_rejects_upper_bound() -> None:
    highest_valid = _packed_number(
        len(BASE_THEMES) - 1,
        len(COLOR_THEMES),
        len(COLOR_THEMES),
        len(STYLE_REGISTRY) - 1,
        len(FONT_REGISTRY) - 1,
        len(RADIUS_OPTIONS) - 1,
    )
    assert highest_valid == SEED_SPACE_SIZE - 1
    assert decode_seed(_seed_for_number(highest_valid)) == {
        "baseId": BASE_THEMES[-1]["id"],
        "colorId": COLOR_THEMES[-1]["id"],
        "chartId": COLOR_THEMES[-1]["id"],
        "styleId": STYLE_REGISTRY[-1]["id"],
        "fontId": FONT_REGISTRY[-1]["id"],
        "radius": RADIUS_OPTIONS[-1][1],
    }
    assert decode_seed(_seed_for_number(SEED_SPACE_SIZE)) is None


def test_default_seed_remains_unchanged() -> None:
    assert decode_seed("b0") == {
        "baseId": BASE_THEMES[0]["id"],
        "colorId": None,
        "chartId": None,
        "styleId": STYLE_REGISTRY[0]["id"],
        "fontId": FONT_REGISTRY[0]["id"],
        "radius": RADIUS_OPTIONS[2][1],
    }


def test_legacy_seed_mapping_change_is_explicit() -> None:
    # This historical payload encoded Plus Jakarta/Luma/Medium with the old
    # font radix of 5; under the accepted new layout it now decodes differently.
    legacy_seed = _seed_for_number(38)

    assert decode_seed(legacy_seed) == {
        "baseId": BASE_THEMES[0]["id"],
        "colorId": None,
        "chartId": None,
        "styleId": STYLE_REGISTRY[0]["id"],
        "fontId": FONT_REGISTRY[9]["id"],
        "radius": RADIUS_OPTIONS[2][1],
    }


def test_generated_javascript_codecs_match_cli_and_cover_shuffle() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the generated seed codecs")

    generated_browser_js = seed_engine().children[0].children[0].contents._var_value
    js_checks = r"""
const cases = [];
for (let fontIndex = 0; fontIndex < _FR.length; fontIndex++) {
  for (let styleIndex = 0; styleIndex < _SR.length; styleIndex++) {
    for (let radiusIndex = 0; radiusIndex < _RO.length; radiusIndex++) {
      const config = {
        '__base_id': _BT[0].id,
        '__color_id': null,
        '__chart_id': null,
        '__style_id': _SR[styleIndex].id,
        '__font_id': _FR[fontIndex].id,
        '--radius': _RO[radiusIndex][1]
      };
      const seed = _encode(config);
      const actionDecoded = _decode(seed);
      const browserDecoded = window.__decodeSeed(seed);
      if (JSON.stringify(actionDecoded) !== JSON.stringify(browserDecoded)) {
        throw new Error(`browser/action mismatch for ${seed}`);
      }
      cases.push({seed, config: actionDecoded});
    }
  }
}

const maximumConfig = {
  '__base_id': _BT[_BT.length - 1].id,
  '__color_id': _CT[_CT.length - 1].id,
  '__chart_id': _CT[_CT.length - 1].id,
  '__style_id': _SR[_SR.length - 1].id,
  '__font_id': _FR[_FR.length - 1].id,
  '--radius': _RO[_RO.length - 1][1]
};
const maximumSeed = _encode(maximumConfig);
if (_b62d(maximumSeed.substring(0, 4)) !== _SEED_SPACE_SIZE - 1 ||
    !_decode(maximumSeed) || !window.__decodeSeed(maximumSeed)) {
  throw new Error('highest valid seed failed');
}
const invalidSeed = _b62e(_SEED_SPACE_SIZE, 4) +
    _b62e((_SEED_SPACE_SIZE * 12345) % 916132832, 5);
if (_decode(invalidSeed) || window.__decodeSeed(invalidSeed)) {
  throw new Error('seed at the upper bound was accepted');
}

Math.random = () => 0.999999999999;
const shuffledSeed = _randomSeed();
if (_b62d(shuffledSeed.substring(0, 4)) !== _SEED_SPACE_SIZE - 1 ||
    !_decode(shuffledSeed)) {
  throw new Error('shuffle did not cover the expanded seed range');
}
console.log(JSON.stringify({cases, maximumSeed}));
"""
    js = (
        "const window = globalThis;\n"
        + _engine_js()
        + "\n"
        + generated_browser_js
        + "\n"
        + js_checks
    )
    result = subprocess.run(
        [node, "-e", js], check=True, capture_output=True, text=True, timeout=30
    )
    payload = json.loads(result.stdout)

    assert len(payload["cases"]) == (
        len(FONT_REGISTRY) * len(STYLE_REGISTRY) * len(RADIUS_OPTIONS)
    )
    for case in payload["cases"]:
        assert decode_seed(case["seed"]) == case["config"]
    assert decode_seed(payload["maximumSeed"]) is not None


def test_fromSeed_canonicalises_b0_collision_partner() -> None:
    # Fails at HEAD: `_fromSeed('caaaoAgaa').__seed` is 'caaaoAgaa'. Passes after
    # the fix: both wrappers assign the canonical 'b0' for the all-default config.
    # This pins the intake canonicalisation that prevents a no-op sidebar action
    # from pushing a spurious history entry (the `caaaoAgaa` -> `b0` URL churn).
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the generated seed codecs")

    js = (
        "const window = globalThis;\n"
        + _engine_js()
        + "\nconst a = _fromSeed('caaaoAgaa', false);\n"
        + "const b = _fromSeed('b0', false);\n"
        + "console.log(JSON.stringify({seed_a: a.__seed, seed_b: b.__seed}));\n"
    )
    result = subprocess.run(
        [node, "-e", js], check=True, capture_output=True, text=True, timeout=30
    )
    out = json.loads(result.stdout)

    assert out["seed_a"] == out["seed_b"] == "b0", (
        f"_fromSeed must canonicalise the b0 collision partner: got {out}; "
        "the all-default config must always expose the canonical 'b0' seed so a "
        "no-op re-encode does not churn the URL via history.pushState"
    )


def test_generateFromSeed_canonicalises_b0_collision_partner() -> None:
    # Companion to the wrapper test above, pinning the parallel `generateFromSeed`
    # in `app/engine/seed.py` (the generator invoked by the `popstate` handler).
    # Fails at HEAD (seed_a='caaaoAgaa'); passes after the lockstep fix (both 'b0').
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the generated seed codecs")

    # Capture the rendered seed_engine() script via an rx.script spy so the
    # test exercises the real rendered output rather than the seed.py wrapper
    # in isolation.
    captured: list[str] = []

    def _spy(s: str) -> str:
        captured.append(s)
        return s

    orig_script = rx.script
    rx.script = _spy
    try:
        seed_engine()
    finally:
        rx.script = orig_script
    generated_browser_js = captured[0]

    js = (
        "const window = globalThis;\n"
        + generated_browser_js
        + "\nconst a = window.__generateFromSeed('caaaoAgaa', false);\n"
        + "const b = window.__generateFromSeed('b0', false);\n"
        + "console.log(JSON.stringify({seed_a: a.__seed, seed_b: b.__seed}));\n"
    )
    result = subprocess.run(
        [node, "-e", js], check=True, capture_output=True, text=True, timeout=30
    )
    out = json.loads(result.stdout)

    assert out["seed_a"] == out["seed_b"] == "b0", (
        f"generateFromSeed must canonicalise the b0 collision partner: got {out}; "
        "this keeps the popstate handler on the canonical seed so Back-traversal "
        "to a stale `caaaoAgaa` entry does not re-establish the URL churn"
    )


def test_init_load_then_noop_then_popstate_canonicalises_across_deployed_fstrings() -> (
    None
):
    # Integration regression: exercises the REAL INITIAL_LOAD_JS + APPLY_BASE_PRIMARY_JS
    # f-strings plus the REAL url_sync.py popstate handler and seed.py generateFromSeed
    # (extracted via an rx.script spy), against stubbed window/history/location/document.
    # Fails at HEAD (url stays `?preset=caaaoAgaa`, no-op grows the history stack 1 -> 2,
    # popstate restores the raw non-canonical seed); passes after the fix (intake and
    # popstate both canonicalise to `b0`, the no-op's dedup guard short-circuits).
    #
    # This variant stubs `_setTheme:()=>{}` (matching the bug report's Evidence §7 harness)
    # so the popstate handler runs to completion even though `_client_state_setTheme` is
    # not a registered ClientStateVar in production. The companion test
    # `test_..._production_no_setTheme` mirrors the real-app scenario where
    # `_setTheme` is undefined and the popstate handler must reach the
    # canonicalisation lines via the reorder + try/catch guard in the fix.
    _assert_init_load_noop_popstate_contract(stub_set_theme=True)


def test_init_load_then_noop_then_popstate_canonicalises_in_production_no_setTheme() -> (
    None
):
    # Production-mirror variant of the integration regression above. The live Reflex
    # app does NOT register a `theme` ClientStateVar in app/hooks.py, so
    # `window.refs['_client_state_setTheme']` is undefined in production, and the
    # popstate handler's unguarded `setTheme(config)` call throws TypeError.
    #
    # At HEAD this throw aborts the popstate handler BEFORE `setSeed` /
    # `__updatePresetURL` run, leaving a Back-traversal's stale `caaaoAgaa` URL
    # uncannonicalised and re-establishing the no-op churn. After the fix the
    # reorder + try/catch in url_sync.py's popstate handler makes
    # `setSeed(cs)` + `__updatePresetURL(cs, false)` reachable even when
    # `setTheme` throws, so the canonicalisation still takes effect.
    #
    # Verified against the live dev server (Playwright + headless Chromium):
    # `pageerror: window.refs._client_state_setTheme is not a function` fires
    # on `go_back()`/`go_forward()`, and the URL stays at the stale entry's
    # value at HEAD but is canonicalised to `?preset=b0` after the fix.
    _assert_init_load_noop_popstate_contract(stub_set_theme=False)


def _assert_init_load_noop_popstate_contract(*, stub_set_theme: bool) -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the generated seed codecs")

    # Capture the rendered url_sync + seed scripts the components actually ship.
    captured: dict[str, list[str]] = {}
    orig_script = rx.script

    def spy(s: str) -> str:
        captured.setdefault("s", []).append(s)
        return s

    rx.script = spy
    try:
        seed_engine()
        url_sync_engine()
    finally:
        rx.script = orig_script
    assert len(captured["s"]) == 2, "expected one rx.script call per engine"
    seed_js, url_sync_js = captured["s"]

    set_theme_stub = " '_client_state_setTheme':()=>{}," if stub_set_theme else ""
    stubs = (
        "const window = globalThis;\n"
        "const _pop = [];\n"
        "window.addEventListener = (e, fn) => { if (e === 'popstate') _pop.push(fn); };\n"
        "const _loc = { search: '?preset=caaaoAgaa' };\n"
        "function _sync(u){ const s=(typeof u==='string')?u:(u&&u.href)?u.href:''; "
        "const i=s.indexOf('?'); _loc.search = i>=0?s.slice(i):''; }\n"
        "const _hist = { entries: [{state:{preset:'caaaoAgaa'},url:'https://x/?preset=caaaoAgaa'}], idx: 0,\n"
        "  pushState(s,_,u){ this.entries.push({state:s,url:u}); this.idx=this.entries.length-1; _sync(u); },\n"
        "  replaceState(s,_,u){ if(this.idx<0){this.entries.push({state:s,url:u}); this.idx=0;} "
        "else { this.entries[this.idx]={state:s,url:u}; } _sync(u); } };\n"
        "window.history = _hist; window.location = _loc;\n"
        "class URL { constructor(l){ this._s=l.search; } get search(){ return this._s; }"
        " get searchParams(){ const self=this; return { get(k){ const s=self._s.replace('?',''); "
        "if(!s) return null; for(const kv of s.split('&')){const [kk,vv]=kv.split('='); "
        "if(kk===k) return vv;} return null; },"
        " set(k,v){ let s=self._s.replace('?',''); const p=s?s.split('&'):[]; "
        "const i=p.findIndex(x=>x.startsWith(k+'=')); if(i>=0) p[i]=k+'='+v; else p.push(k+'='+v); "
        "self._s='?'+p.join('&'); } }; }"
        " set(k,v){ this.searchParams.set(k,v); } get href(){ return 'https://x/'+this._s; } }\n"
        "window.URL = URL;\n"
        "const document = { documentElement: { classList: { contains(){return false;}, add(){}, "
        "remove(){} }, style: { setProperty(){}, getPropertyValue(){return '';} } }, "
        "getElementById(){ return null; } };\n"
        "window.document = document;\n"
        "const _ls = { _d:{}, getItem(k){return this._d[k]||null;}, setItem(k,v){this._d[k]=v;} }; "
        "window.localStorage = _ls;\n"
        "window.matchMedia = () => ({ matches: false });\n"
        "const refs = { '_client_state_seed': null,"
        " '_client_state_setSeed': (s) => { refs['_client_state_seed'] = s; },"
        " '_client_state_setDarkmode':()=>{}, '_client_state_setWelcome_open':()=>{},"
        f"{set_theme_stub}"
        " '_client_state_setBase_theme_color':()=>{},"
        " '_client_state_setSelected_base_color_cs':()=>{}, '_client_state_setTheme_color':()=>{},"
        " '_client_state_setSelected_theme_cs':()=>{}, '_client_state_setChart_color':()=>{},"
        " '_client_state_setSelected_chart_cs':()=>{}, '_client_state_setSelected_style_cs':()=>{},"
        " '_client_state_setSelected_font_cs':()=>{}, '_client_state_setSelected_radius_cs':()=>{},"
        " '_client_state_darkmode': false };\n"
        "window.refs = refs;\n"
        "const _timers = []; window.setTimeout = (fn) => { _timers.push(fn); };\n"
    )

    js = (
        stubs
        + _engine_js()
        + "\n"
        + seed_js
        + "\n"
        + url_sync_js
        + "\n"
        + INITIAL_LOAD_JS
        + "\n"
        + "_timers.forEach(t => t());\n"
        + "const url_after_init = _loc.search;\n"
        + "const entries_after_init = _hist.entries.length;\n"
        + APPLY_BASE_PRIMARY_JS
        + "\n"
        + "const entries_after_noop = _hist.entries.length;\n"
        # Phase 3: a pre-existing stale caaaoAgaa history entry (e.g. one minted
        # before the fix shipped, or surfaced via Back). popstate must re-canonicalise
        # it rather than restore the raw non-canonical seed into state/URL.
        + "_hist.entries = [{state:{preset:'caaaoAgaa'},url:'https://x/?preset=caaaoAgaa'}]; "
        + "_hist.idx = 0; _sync('https://x/?preset=caaaoAgaa'); "
        + "refs['_client_state_seed'] = 'b0';\n"
        + "try { _pop.forEach(fn => fn({ state: { preset: 'caaaoAgaa' } })); } "
        + "catch (e) { console.error('popstate dispatched:', e && e.message); "
        + "throw e; }\n"
        + "const seed_after_popstate = refs['_client_state_seed'];\n"
        + "const url_after_popstate = _loc.search;\n"
        + "console.log(JSON.stringify({url_after_init, entries_after_init, "
        + "entries_after_noop, seed_after_popstate, url_after_popstate}));\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(js)
    script_path = tf.name
    try:
        result = subprocess.run(
            [node, script_path], check=True, capture_output=True, text=True, timeout=30
        )
    finally:
        os.unlink(script_path)
    out = json.loads(result.stdout)

    assert out["url_after_init"] == "?preset=b0", (
        f"INITIAL_LOAD must canonicalise ?preset=caaaoAgaa to b0; "
        f"got url={out['url_after_init']!r}"
    )
    assert out["entries_after_init"] == 1, (
        f"INITIAL_LOAD replaceState must keep exactly one history entry "
        f"(the initial document entry); got {out['entries_after_init']}"
    )
    assert out["entries_after_noop"] == out["entries_after_init"], (
        f"no-op APPLY_BASE_PRIMARY_JS must not grow the history stack (the dedup "
        f"guard must short-circuit); history grew "
        f"{out['entries_after_init']} -> {out['entries_after_noop']}"
    )
    assert out["seed_after_popstate"] == "b0", (
        f"popstate handler must canonicalise a stale caaaoAgaa entry to b0 in "
        f"state; got seed={out['seed_after_popstate']!r}"
    )
    assert out["url_after_popstate"] == "?preset=b0", (
        f"popstate handler must replaceState the URL to b0; "
        f"got url={out['url_after_popstate']!r}"
    )


def test_b0_is_the_only_encode_after_decode_asymmetry() -> None:
    # Contract test (future-proofing, NOT regression coverage for the fix above):
    # pins the single documented canonicalisation asymmetry (the `return 'b0'`
    # shortcut in `_encode`). PASSES at HEAD and after the fix, because both
    # preserve the shortcut. FAILS only if a registry/formula change introduces
    # a NEW seed that decodes to a config whose deployed re-encode differs from
    # itself — i.e. a new member of the collision class.
    #
    # NOTE: `_decode` returns camelCase keys (baseId, colorId, ...) while `_encode`
    # reads `__`-prefixed keys, so the bare `_encode(_decode(seed))` returns null
    # for every seed. The key translation below mirrors what `_rebuild` produces
    # in the deployed direction (`_fromSeed -> _rebuild -> _encode`, what
    # APPLY_BASE_PRIMARY_JS actually runs).
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the generated seed codecs")

    js = (
        "const window = globalThis;\n"
        + _engine_js()
        + "\nconst out = [];\n"
        + "for (let n = 0; n < _SEED_SPACE_SIZE; n++) {\n"
        + "  const seed = _b62e(n, 4) + _b62e((n * 12345) % 916132832, 5);\n"
        + "  const cfg = _decode(seed);\n"
        + "  if (!cfg) continue;\n"
        + "  const enc = _encode({\n"
        + "    '__base_id': cfg.baseId, '__color_id': cfg.colorId, "
        + "'__chart_id': cfg.chartId,\n"
        + "    '__style_id': cfg.styleId, '__font_id': cfg.fontId, "
        + "'--radius': cfg.radius,\n"
        + "  });\n"
        + "  if (enc !== seed) out.push({ n: n, seed: seed, enc: enc });\n"
        + "}\n"
        + "console.log(JSON.stringify(out));\n"
    )
    result = subprocess.run(
        [node, "-e", js], check=True, capture_output=True, text=True, timeout=30
    )
    violations = json.loads(result.stdout)

    assert violations == [{"n": 2, "seed": "caaaoAgaa", "enc": "b0"}], (
        f"expected exactly the single b0 canonicalisation asymmetry, got "
        f"{violations}; a new entry means a registry/formula change introduced a "
        f"new encode-after-decode collision (the intake canonicalisation in "
        f"_fromSeed/generateFromSeed would not cover it)"
    )
