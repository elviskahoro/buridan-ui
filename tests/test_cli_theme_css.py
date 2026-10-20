"""Regression coverage for CLI-generated theme CSS radius variables.

The CLI injects a Tailwind ``borderRadius`` config mapping
``rounded-sm``..``rounded-4xl`` to ``var(--radius-sm)``..``var(--radius-4xl)``,
so ``generate_theme_css()`` must emit a derived ``@theme inline`` radius scale
defining those variables from the base ``--radius``. Without it, every
``buridan init`` + ``buridan apply`` project silently renders ``rounded-*``
utilities with square corners (Tailwind v4 compiles without warnings).

These tests pin the invariants that are easy to silently regress:
- the radius scale block is emitted exactly once by ``generate_theme_css``,
- it stays byte-equivalent to the repo's hand-authored ``assets/globals.css``,
- ``cmd_apply`` writes it to ``assets/globals.css`` and does not duplicate it
  on re-apply,
- ``cmd_apply`` leaves the shimmer/scrollbar utility ``@theme inline`` blocks
  added by ``cmd_init`` untouched.
"""  # noqa: INP001

from __future__ import annotations

import re
from pathlib import Path

import pytest

from cli.main import RADIUS_SCALE_BLOCK, cmd_apply, cmd_init, generate_theme_css

ROOT_DIR = Path(__file__).parent.parent
REPO_GLOBALS_CSS = ROOT_DIR / "assets" / "globals.css"

EXPECTED_RADIUS_VARS = {
    "--radius-sm": "calc(var(--radius) * 0.6)",
    "--radius-md": "calc(var(--radius) * 0.8)",
    "--radius-lg": "var(--radius)",
    "--radius-xl": "calc(var(--radius) * 1.4)",
    "--radius-2xl": "calc(var(--radius) * 1.8)",
    "--radius-3xl": "calc(var(--radius) * 2.2)",
    "--radius-4xl": "calc(var(--radius) * 2.6)",
}


@pytest.fixture
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A minimal Reflex project root with an rxconfig.py."""
    (tmp_path / "rxconfig.py").write_text(
        'import reflex as rx\nconfig = rx.Config(app_name="t")\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize(("var", "value"), sorted(EXPECTED_RADIUS_VARS.items()))
def test_generate_theme_css_emits_each_derived_radius(var: str, value: str) -> None:
    css = generate_theme_css("b0")
    assert f"{var}: {value};" in css, f"missing derived radius var {var}"


def test_generate_theme_css_emits_root_and_dark_blocks_unchanged() -> None:
    """The fix must not disturb the existing :root / .dark block shape, and
    the base --radius must still be emitted in both.
    """
    css = generate_theme_css("b0")
    assert css.startswith(":root {")
    assert "\n.dark {" in css
    assert css.count("--radius: 0.625rem;") == 2  # noqa: PLR2004
    assert css.count("@theme inline {") == 1


def test_generate_theme_css_radius_scale_matches_repo_globals_css() -> None:
    """The CLI-emitted radius block must stay byte-equivalent (modulo
    whitespace) to the hand-authored one in assets/globals.css so generated
    projects match the in-repo demo.
    """
    repo_css = REPO_GLOBALS_CSS.read_text(encoding="utf-8")
    m = re.search(r"@theme inline \{[^@]*?--radius-4xl[^\n]*\n\}", repo_css)
    assert m is not None, "repo assets/globals.css no longer has a radius scale block"
    repo_block = m.group(0)

    def norm(s: str) -> str:
        return s.replace(" ", "").replace("\n", "")

    assert norm(RADIUS_SCALE_BLOCK) == norm(repo_block)


def test_cmd_apply_writes_radius_scale_to_globals_css(project_dir: Path) -> None:
    cmd_apply("b0")
    css = (project_dir / "assets" / "globals.css").read_text(encoding="utf-8")
    assert "@theme inline {" in css
    for var, value in EXPECTED_RADIUS_VARS.items():
        assert f"{var}: {value};" in css


def test_cmd_apply_is_idempotent_for_radius_scale(project_dir: Path) -> None:
    cmd_apply("b0")
    cmd_apply("b0")
    css = (project_dir / "assets" / "globals.css").read_text(encoding="utf-8")
    assert css.count("@theme inline {") == 1
    assert css.count("--radius-sm") == 1
    assert css.count(":root {") == 1
    assert css.count(".dark {") == 1


def test_cmd_apply_preserves_utility_theme_inline_blocks(project_dir: Path) -> None:
    """shimmer/scrollbar utilities define their own @theme inline keyframe
    blocks; cmd_apply must not corrupt or duplicate them, and re-applying a
    preset must not accumulate extra radius blocks alongside them.
    """
    cmd_init()
    after_init = (project_dir / "assets" / "globals.css").read_text(encoding="utf-8")
    assert after_init.count("@theme inline {") >= 2  # noqa: PLR2004

    cmd_apply("b0")
    after_apply = (project_dir / "assets" / "globals.css").read_text(encoding="utf-8")
    assert after_apply.count("@theme inline {") == 3  # noqa: PLR2004
    assert after_apply.count("--radius-sm") == 1
    assert "tw-shimmer" in after_apply
    assert "scroll-fade-reveal-t" in after_apply

    cmd_apply("b0")
    after_reapply = (project_dir / "assets" / "globals.css").read_text(encoding="utf-8")
    assert after_reapply.count("@theme inline {") == 3  # noqa: PLR2004
    assert after_reapply.count("--radius-sm") == 1
    assert "tw-shimmer" in after_reapply
    assert "scroll-fade-reveal-t" in after_reapply
