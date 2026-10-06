"""Regression coverage for `--USAGE(...)--` and `--CODE_FILE(...)--` rendering in
``DocParser``.

Background: components exported as ``name = Class.create`` (bound classmethods)
were routed through the ``inspect_obj = obj.__class__`` fallback, which
substitutes the builtin ``<class 'method'>`` for the bound method. That made
``inspect.getfile`` raise (silently blanking ``file_path``) and causing the
``usage`` branch to emit the bogus import ``from components.ui.component import
<name>`` (the module ``components/ui/component.py`` does not exist). The same
substitution also made ``inspect.getmodule`` + ``inspect.getsource`` raise along
the ``code_file`` branch, rendering a visible parse-error element.

These tests guard the fix for both consumers and stay in sync with the registry
and the shipped docs (so any future bound-classmethod component is covered
without per-component test churn).
"""

import glob
import importlib
import inspect
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pytest

from app.www import constants
from app.www.parser import DocParser

USAGE_IMPORT_RE = re.compile(r"from components\.ui\.(\w+) import (\w+)")
USAGE_DIRECTIVE_RE = re.compile(r"--USAGE\(([^)]+)\)--")


@pytest.fixture(scope="module")
def parser() -> DocParser:
    return DocParser(
        dynamic_load_dirs=[constants.DOCS_LIBRARY_ROOT, constants.COMPONENTS_ROOT]
    )


# Components exported as ``name = Class.create`` (bound classmethods) are the
# population affected by the bug; any future component added this way must also
# render a real, importable module path (not the ``"component"`` fallback).
BOGUS_FALLBACK = "components.ui.component"


def _registry_entry(parser: DocParser, name: str) -> tuple[Callable, str]:
    """Return the ``(obj, preferred_name)`` tuple the parser stores for ``name``.

    ``DocParser.registry`` is loosely annotated as ``dict[str, Callable]`` even
    though it stores ``(obj, preferred_name)`` tuples; this helper isolates the
    single ``cast`` needed to bridge that annotation.
    """
    return cast(tuple[Callable, str], parser.registry[name])


def _usage_import_path(parser: DocParser, name: str) -> str:
    rendered = str(parser._render("usage", name))
    match = USAGE_IMPORT_RE.search(rendered)
    assert match is not None, (
        f"no `from components.ui.<module> import <name>` line rendered for "
        f"{name!r}: {rendered!r}"
    )
    return match.group(0)


def test_every_bound_classmethod_in_registry_renders_real_importable_module(
    parser: DocParser,
) -> None:
    """Every component registered as a bound classmethod (``name = Class.create``)
    must render a ``usage`` import path whose module (a) is not the
    ``components.ui.component`` fallback and (b) is actually importable with the
    rendered symbol. Dynamic so any future bound-classmethod component is covered.
    """
    bound = sorted(
        n for n in parser.registry if inspect.ismethod(_registry_entry(parser, n)[0])
    )
    assert bound, "expected at least one bound-classmethod component in the registry"
    for name in bound:
        preferred = _registry_entry(parser, name)[1]
        import_path = _usage_import_path(parser, name)
        assert BOGUS_FALLBACK not in import_path, (
            f"--USAGE({name})-- rendered bogus fallback {import_path!r}"
        )
        match = USAGE_IMPORT_RE.search(import_path)
        assert match is not None, f"unmatched import path: {import_path!r}"
        module_stem, symbol = match.group(1), match.group(2)
        assert module_stem == name, (
            f"usage module stem {module_stem!r} should match symbol {name!r}"
        )
        assert symbol == preferred, (
            f"usage import name {symbol!r} should match preferred {preferred!r}"
        )
        module = importlib.import_module(f"components.ui.{module_stem}")
        assert hasattr(module, symbol), (
            f"{module.__name__}.{symbol} not importable for {name!r}"
        )


def test_every_shipped_usage_directive_renders_importable_module(
    parser: DocParser,
) -> None:
    """End-to-end: every ``--USAGE(arg)--`` directive shipped in
    ``docs/components/*.md`` must produce a valid, importable import line and must
    not emit the ``components.ui.component`` fallback."""
    docs = sorted(glob.glob(str(ROOT_DIR / "docs" / "components" / "*.md")))
    assert docs, "expected docs/components/*.md files to exist"
    seen: set[str] = set()
    for doc in docs:
        for m in USAGE_DIRECTIVE_RE.finditer(Path(doc).read_text()):
            arg = m.group(1).strip()
            seen.add(arg)
            import_path = _usage_import_path(parser, arg)
            assert BOGUS_FALLBACK not in import_path, (
                f"directive --USAGE({arg})-- rendered bogus fallback {import_path!r}"
            )
            match = USAGE_IMPORT_RE.search(import_path)
            assert match is not None, f"unmatched import path: {import_path!r}"
            module = importlib.import_module(f"components.ui.{match.group(1)}")
            assert hasattr(module, match.group(2)), (
                f"{match.group(1)}.{match.group(2)} not importable for {arg!r}"
            )
    assert seen, "no --USAGE(...)-- directives found in docs/components/*.md"


def test_bound_classmethod_code_file_renders_source_not_parse_error(
    parser: DocParser,
) -> None:
    """``--CODE_FILE(<bound-method>)--`` is a latent footgun: no shipped doc
    currently exercises it, but the same ``inspect_obj`` substitution that broke
    ``--USAGE(...)--`` also made ``inspect.getmodule`` + ``inspect.getsource``
    raise here, surfacing a red parse-error element. Pin one representative so a
    future ``--CODE_FILE(button)--`` directive does not silently regress."""
    rendered = str(parser._render("code_file", "button"))
    assert "Error in code_file" not in rendered
    assert "text-red-500" not in rendered


def test_unknown_component_still_reports_visible_not_found_error(
    parser: DocParser,
) -> None:
    """The fix must not re-silence the visible ``'<name>' not found`` error path
    for genuinely unregistered names — that loud-failure behavior is what
    originally surfaced (before commit e102215) for the bound-classmethod
    components, and it must remain for unknown names."""
    rendered = str(parser._render("usage", "this_component_does_not_exist"))
    assert "not found" in rendered
    assert "text-red-500" in rendered
