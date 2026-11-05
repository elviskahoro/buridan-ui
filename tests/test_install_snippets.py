"""Regression tests for the install CLI snippet emitted by docs generators.

The component docs surface a "CLI" install command in two places:

1. As static markdown rendered by ``scripts/generate_markdown.py`` into
   ``assets/docs/components/*.md`` (the markdown shipped to non-JS doc
   consumers, including the README + static mirrors).
2. As a live Reflex component rendered by ``app/www/parser.py`` on the docs
   website (``cli_and_manual_installation_wrapper``).

Both used to emit ``buridan add component <name>``. The ``buridan add``
subparser has always taken bare component names as positional args
(``nargs="+"``), and the July 2026 registry restructure (commit 9321f4b)
removed the ``component`` registry key, so the documented command was being
looked up as the bogus component name ``component`` -- the CLI printed
``Warning: Component 'component' not found in registry.`` on every install,
but still succeeded (the failure is non-fatal), which masked the regression.

These tests pin both templates and the generated outputs to the correct
``buridan add <name>`` syntax the ``add`` subparser actually supports, and
guard against the stale ``add component`` qualifier coming back.
"""  # noqa: INP001

import pathlib
import re
import sys

import pytest

# ---------------------------------------------------------------------------
# Paths — the repo root isn't a package, so put it on sys.path explicitly.
# ---------------------------------------------------------------------------
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www import (  # noqa: E402
    constants,
    parser as parser_module,
)
from app.www.parser import DocParser  # noqa: E402
from scripts import generate_markdown as generator_module  # noqa: E402

GENERATOR_PATH = pathlib.Path(generator_module.__file__)
PARSER_PATH = pathlib.Path(parser_module.__file__)
COMPONENTS_DOCS_DIR = ROOT_DIR / "assets" / "docs" / "components"

# The stale install-command qualifier we must never re-introduce. Anchored
# to the ``buridan add component`` prefix specifically: ``buridan add
# components`` (plural, as in the English sentence "add components to your
# project") and ``uv run buridan add <name>`` (correct) must not match.
_STALE_INSTALL_PATTERN = re.compile(r"buridan add component\b")

# The CLI an installed component name must produce. The install command
# always lives directly under a ``### CLI`` heading followed by a fenced
# ``bash`` block, so the regex anchors to that shape and captures the
# component name argument.
_INSTALL_COMMAND_PATTERN = re.compile(
    r"^### CLI\s+```bash\nburidan add (?P<name>\w+)\n```",
    re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_component_registry() -> generator_module.Registry:
    """Load the real component registry the markdown generator uses.

    Used so the install-directive path actually exercises the same fallback
    branch the 34 shipped docs hit (no docs source passes an explicit
    ``cli_command``, so every install directive falls through to the
    fallback template -- the exact code path that regressed).
    """
    return generator_module.dynamic_load_components(
        generator_module.DYNAMIC_LOAD_DIRS,
    )


# ---------------------------------------------------------------------------
# Source-level guards: catch the stale template string re-entering either file
# ---------------------------------------------------------------------------


def test_generator_template_has_no_stale_add_component_qualifier() -> None:
    """``scripts/generate_markdown.py`` must not embed ``buridan add component``.

    The install fallback builds the command from ``buridan add <name>``:
    qualifying the name with a ``component`` sub-keyword would be looked up
    as a component name itself and trigger a spurious registry warning. This
    scan catches the literal stale template string being re-introduced.
    """
    source = GENERATOR_PATH.read_text(encoding="utf-8")
    offenders = _STALE_INSTALL_PATTERN.findall(source)
    assert offenders == [], (
        f"stale `buridan add component` template re-introduced in "
        f"{GENERATOR_PATH.relative_to(ROOT_DIR)}"
    )


def test_parser_template_has_no_stale_add_component_qualifier() -> None:
    """``app/www/parser.py`` must not embed ``buridan add component``.

    Same regression as the markdown generator, but for the live docs site
    install command (prefixed with ``uv run`` to match the project's run
    convention). Anchored to ``buridan add component`` so the surrounding
    ``uv run`` does not affect detection.
    """
    source = PARSER_PATH.read_text(encoding="utf-8")
    offenders = _STALE_INSTALL_PATTERN.findall(source)
    assert offenders == [], (
        f"stale `buridan add component` template re-introduced in "
        f"{PARSER_PATH.relative_to(ROOT_DIR)}"
    )


# ---------------------------------------------------------------------------
# generate_markdown.py end-to-end: --INSTALL(name)-- → markdown CLI snippet
# ---------------------------------------------------------------------------


def test_install_directive_renders_bare_component_name() -> None:
    """The fallback install template must emit ``buridan add <name>``.

    ``button`` exercises the actual fallback path (no docs source passes an
    explicit ``cli_command``), so this is the exact regression -- previously
    produced ``buridan add component button``.
    """
    registry = _load_component_registry()
    assert "button" in registry, "fixture component `button` not in registry"

    output = generator_module.convert_to_pure_markdown(
        "--INSTALL(button)--",
        registry,
    )
    assert "buridan add button" in output
    assert "buridan add component" not in output
    # `button` must appear as the only positional arg between `buridan add`
    # and the closing fence; ``component button`` would match this regex
    # too, so the explicit no-`component` assertion above is the real guard.
    match = _INSTALL_COMMAND_PATTERN.search(output)
    assert match, f"CLI snippet missing or malformed in output:\n{output}"
    assert match.group("name") == "button"


def test_install_directive_preserves_explicit_cli_command_override() -> None:
    """The two-tuple form ``--INSTALL(["Name", "custom cli"])--`` still wins.

    The fallback is only a fallback -- when a docs source passes an explicit
    ``cli_command`` it must be honored unchanged. Guards against over-correcting
    the fallback and accidentally dropping the override branch.
    """
    registry = _load_component_registry()

    output = generator_module.convert_to_pure_markdown(
        '--INSTALL(["button", "buridan add button --force"])--',
        registry,
    )
    assert "buridan add button --force" in output
    assert "buridan add component" not in output


# ---------------------------------------------------------------------------
# parser.py end-to-end: --INSTALL(name)-- → live Reflex CLI tab
# ---------------------------------------------------------------------------


def test_parser_install_renders_bare_component_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``DocParser._render("install", "button")`` passes ``uv run buridan add
    button`` to ``cli_and_manual_installation_wrapper`` -- not the stale
    ``... add component button`` form. Captures the cli_cmd argument via
    mocking the wrapper so the test does not depend on Reflex's string
    rendering.
    """
    captured: dict[str, object] = {}

    def fake_wrapper(
        cli_cmd: str,
        files_data: list[tuple[str, str]],
    ) -> object:
        captured["cli_cmd"] = cli_cmd
        captured["files_data"] = files_data
        return object()

    monkeypatch.setattr(
        parser_module,
        "cli_and_manual_installation_wrapper",
        fake_wrapper,
    )

    parser = DocParser(dynamic_load_dirs=[constants.COMPONENTS_ROOT])
    assert "button" in parser.registry, "fixture component `button` not in registry"

    parser._render("install", "button")  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    assert captured["cli_cmd"] == "uv run buridan add button"
    # Sanity: files_data is populated (the install wrapper would otherwise
    # render an empty Manual tab, hiding a regression where the install path
    # short-circuited before collecting files).
    assert captured["files_data"], "install wrapper got empty files_data"


# ---------------------------------------------------------------------------
# Generated docs sweep: every shipped component install snippet uses the
# correct syntax and none advertises the broken command
# ---------------------------------------------------------------------------


def _all_component_docs() -> list[pathlib.Path]:
    """Every shipped component doc under assets/docs/components/."""
    return sorted(COMPONENTS_DOCS_DIR.glob("*.md"))


def test_no_generated_component_doc_advertises_stale_add_component() -> None:
    """No shipped ``assets/docs/components/*.md`` may contain the stale
    ``buridan add component`` template. The 34 docs that previously carried
    it must all be regenerated to the correct syntax. Catches the precise
    regression this PR fixes: if a future change reverts the templates AND
    regenerates the docs, CI's ``git diff --exit-code assets/docs`` would
    pass (both sides reverted together), so this source-side sweep is the
    only guard.
    """
    offenders: list[str] = []
    for doc in _all_component_docs():
        text = doc.read_text(encoding="utf-8")
        if _STALE_INSTALL_PATTERN.search(text):
            offenders.append(str(doc.relative_to(ROOT_DIR)))
    assert offenders == [], (
        "stale `buridan add component` install command still present in:\n  "
        + "\n  ".join(offenders)
    )
