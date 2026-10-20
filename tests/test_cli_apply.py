"""Regression coverage for ``buridan apply`` (``cmd_apply``) theme rewriting.

The replace path — re-applying a preset over a file that already contains a
``:root {`` / ``.dark {`` theme block — must preserve the *entire* surrounding
file: content above the theme block, the freshly generated theme block, and
content below the theme block. Re-applying a preset to switch themes is the
documented workflow surfaced by https://buridan-ui.com/create (see
``cli/README.md`` and ``app/templates/compiler.py``, which emits
``uv run buridan apply --preset {seed}`` into generated project templates).

Git blame traces the original data-loss bug to commit ``8dc954c`` which added
``cmd_apply``: on re-apply it rebuilt the file as ``theme_css + after`` and
silently dropped ``lines[:start_line]`` — every ``@import``/``@tailwind``
directive and hand-written rule sitting above the theme block was destroyed.
"""

import sys
from pathlib import Path

import pytest

from cli.main import CHARS, cmd_apply, generate_theme_css, main

# ── valid preset seeds ──────────────────────────────────────────────────────────


def _to_base62(value: int, width: int) -> str:
    """Encode an integer using the seed codec's fixed-width base-62 alphabet."""
    out = ""
    for _ in range(width):
        out += CHARS[value % 62]
        value //= 62
    return out


def _seed_for_number(number: int) -> str:
    """Encode a packed config number into a valid 9-char preset seed."""
    checksum = (number * 12345) % 916132832
    return _to_base62(number, 4) + _to_base62(checksum, 5)


_PRESET_A = "b0"
_PRESET_B = _seed_for_number(0)
_THEME_A = generate_theme_css(_PRESET_A)
_THEME_B = generate_theme_css(_PRESET_B)

# A custom placeholder theme distinct from any generated preset. Used to detect
# whether ``cmd_apply`` actually REPLACES the block (not merely appends to it):
# the ``--marker`` declarations must disappear after a real apply.
_CUSTOM_THEME = (
    ":root {\n"
    "    --marker: light-sentinel;\n"
    "}\n"
    "\n"
    ".dark {\n"
    "    --marker: dark-sentinel;\n"
    "}"
)

# Content a user keeps above the theme block (font imports, Tailwind v4
# directives, hand-written rules). No trailing newline — keeps ``before`` an
# identity after ``"\n".join(lines[:start_line]).rstrip("\n")``.
_PREFIX = (
    '@import url("https://fonts.googleapis.com/css2?family=Inter");\n'
    "@tailwind base;\n"
    "@tailwind components;\n"
    "@tailwind utilities;\n"
    "\n"
    "/* custom user variables kept outside the theme block */\n"
    "::selection {\n"
    "    background: var(--foreground);\n"
    "    color: var(--background);\n"
    "}\n"
    "\n"
    "body {\n"
    "    background-color: var(--background);\n"
    "}"
)

# Content a user keeps below the theme block (utility classes appended by init
# or hand-written). No leading newline — keeps ``after`` an identity after
# ``"\n".join(lines[end_line + 1:]).lstrip("\n")``.
_SUFFIX = (
    "/* user utility blocks appended after the theme */\n"
    ".my-card {\n"
    "    border-radius: var(--radius);\n"
    "    padding: var(--card-padding);\n"
    "}\n"
    "\n"
    ".hidden-thing {\n"
    "    display: none;\n"
    "}"
)


# ── fixtures ────────────────────────────────────────────────────────────────────


@pytest.fixture
def reflex_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a minimal Reflex project root in a temp dir and chdir into it."""
    (tmp_path / "rxconfig.py").write_text("import reflex as rx\nconfig = rx.Config()\n")
    (tmp_path / "assets").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _globals(root: Path) -> Path:
    return root / "assets" / "globals.css"


def _write_globals(root: Path, content: str) -> None:
    _globals(root).write_text(content)


def _read_globals(root: Path) -> str:
    return _globals(root).read_text()


# ── tests: re-apply preserves surrounding content (the bug) ────────────────────


def test_reapply_preserves_content_above_and_below_root_block(
    reflex_project: Path,
) -> None:
    """Re-applying over a full file (prefix + theme + suffix) preserves the
    prefix and suffix while replacing the theme — no silent data loss.
    """
    _write_globals(reflex_project, _PREFIX + "\n\n" + _CUSTOM_THEME + "\n\n" + _SUFFIX)
    cmd_apply(_PRESET_A)
    result = _read_globals(reflex_project)

    assert result == _PREFIX + "\n\n" + _THEME_A + "\n\n" + _SUFFIX + "\n"
    assert "--marker" not in result
    assert result.count(":root {") == 1
    assert result.count(".dark {") == 1
    assert result.index("@tailwind base;") < result.index(":root {")
    assert result.index(":root {") < result.index(".my-card {")


def test_reapply_is_idempotent(reflex_project: Path) -> None:
    """Applying the same preset twice yields a stable file (no duplication of
    the theme block, no erosion of surrounding content).
    """
    _write_globals(reflex_project, _PREFIX + "\n\n" + _CUSTOM_THEME + "\n\n" + _SUFFIX)
    cmd_apply(_PRESET_A)
    first = _read_globals(reflex_project)
    cmd_apply(_PRESET_A)
    second = _read_globals(reflex_project)
    assert second == first
    assert second.count(":root {") == 1
    assert second.count(".dark {") == 1
    assert "@tailwind base;" in second
    assert ".my-card {" in second


def test_reapply_switching_presets_preserves_surrounding_content(
    reflex_project: Path,
) -> None:
    """Switching presets via re-apply keeps the prefix and suffix and lands on
    the new theme block (the documented workflow from the theme builder).
    """
    assert _THEME_A != _THEME_B, "test presets must produce different themes"

    _write_globals(reflex_project, _PREFIX + "\n\n" + _CUSTOM_THEME + "\n\n" + _SUFFIX)
    cmd_apply(_PRESET_A)
    cmd_apply(_PRESET_B)
    result = _read_globals(reflex_project)

    assert result == _PREFIX + "\n\n" + _THEME_B + "\n\n" + _SUFFIX + "\n"
    assert result.count(":root {") == 1
    assert result.count(".dark {") == 1
    assert "--marker" not in result
    assert "@tailwind base;" in result
    assert ".my-card {" in result


def test_apply_via_cli_entry_point_preserves_prefix(
    reflex_project: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end through the argparse entry point: ``buridan apply --preset``
    must route through cmd_apply and preserve the prefix (no wiring bypass).
    """
    _write_globals(reflex_project, _PREFIX + "\n\n" + _CUSTOM_THEME + "\n\n" + _SUFFIX)
    monkeypatch.setattr(sys, "argv", ["buridan", "apply", "--preset", _PRESET_A])
    main()
    result = _read_globals(reflex_project)
    assert result == _PREFIX + "\n\n" + _THEME_A + "\n\n" + _SUFFIX + "\n"
    assert "--marker" not in result
