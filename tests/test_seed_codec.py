"""Regression coverage for the packed theme preset seed format."""

import json
import shutil
import subprocess

import pytest

from app.engine.actions import _engine_js
from app.engine.seed import seed_engine
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
