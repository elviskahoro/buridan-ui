"""Regression tests for the Prism language class wired by ``render_pre``."""

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest
import reflex as rx

from app.www.style import markdown_component_map, render_pre

ROOT_DIR = Path(__file__).parent.parent
PRISM_JS = ROOT_DIR / "assets" / "prism" / "prism.js"
DOCS_DIR = ROOT_DIR / "docs"

PYTHON_CONTENT_LABELS = [
    "python",
    "reflex",
    "example_chart.py",
    "chart_tooltip.py",
    "chart_example.py",
    "chart",
    "rxconfig.py",
    "rx.App",
    "composition",
    "",
]


def _resolve_language_class(language: str) -> str:
    rendered = str(render_pre("x", language=language).render())
    winning = re.search(r'true \? "(language-[^"]+)"', rendered)
    if winning:
        return winning.group(1)
    fallback = rendered.rfind(': "language-')
    if fallback != -1:
        match = re.search(r'"(language-[^"]+)"', rendered[fallback:])
        if match:
            return match.group(1)
    raise AssertionError(f"no language class resolved for {language!r}")


@pytest.mark.parametrize(
    "language, expected",
    [
        ("python", "language-python"),
        ("bash", "language-bash"),
        ("uv", "language-bash"),
        ("css", "language-css"),
        ("assets/globals.css", "language-css"),
        ("toml", "language-toml"),
        ("pyproject.toml", "language-toml"),
    ],
)
def test_render_pre_wires_prism_class_to_fence_language(
    language: str, expected: str
) -> None:
    assert _resolve_language_class(language) == expected


@pytest.mark.parametrize("language", PYTHON_CONTENT_LABELS)
def test_render_pre_filename_and_section_labels_keep_python(language: str) -> None:
    assert _resolve_language_class(language) == "language-python"


def test_render_pre_production_var_emits_runtime_language_conditional() -> None:
    language = rx.Var(_js_expr="_language", _var_type=str)
    rendered = str(render_pre("x", language=language).render())

    assert "_language" in rendered
    assert '=== "bash"' in rendered
    assert '"language-bash"' in rendered
    assert '=== "css"' in rendered
    assert '"language-css"' in rendered
    assert '=== "toml"' in rendered
    assert '"language-toml"' in rendered
    assert '"language-python"' in rendered
    assert 'className:"language-python"' not in rendered


def test_render_pre_language_conditional_does_not_emit_pyor_helper() -> None:
    language = rx.Var(_js_expr="_language", _var_type=str)
    rendered = str(render_pre("x", language=language).render())

    assert "pyOr" not in rendered


def test_markdown_pre_renderer_uses_runtime_language_for_prism_class() -> None:
    markdown = rx.markdown(
        "```css\nbody { color: red; }\n```",
        component_map=markdown_component_map,
    )
    markdown_component = cast(Any, markdown.children[0])
    pre_renderer = str(markdown_component.format_component_map()["pre"])

    assert "language-(?<lang>.*)" in pre_renderer
    assert "let _language" in pre_renderer
    assert "_language?.valueOf" in pre_renderer
    assert '=== "bash"' in pre_renderer
    assert '=== "css"' in pre_renderer
    assert '=== "toml"' in pre_renderer
    assert '"language-bash"' in pre_renderer
    assert '"language-css"' in pre_renderer
    assert '"language-toml"' in pre_renderer
    assert '"language-python"' in pre_renderer
    assert 'className:"language-python"' not in pre_renderer


def _run_prism_js(assertion_js: str) -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to verify the bundled Prism grammars")
    prism_source = PRISM_JS.read_text(encoding="utf-8")
    js = (
        "var global = globalThis;\n"
        "var window = undefined;\n" + prism_source + "\n" + assertion_js
    )
    result = subprocess.run(
        [node, "-e", js], check=True, capture_output=True, text=True, timeout=30
    )
    return result.stdout


def test_prism_bundle_registers_python_bash_css_toml_grammars() -> None:
    assertion = (
        "const P = global.Prism;\n"
        "const grammars = ['python','py','bash','sh','shell','css','toml'];\n"
        "const missing = grammars.filter(g => typeof P.languages[g] === 'undefined');\n"
        "if (missing.length) throw new Error('missing grammars: ' + missing.join(','));\n"
        "console.log(JSON.stringify(grammars));\n"
    )
    stdout = _run_prism_js(assertion)
    assert set(json.loads(stdout)) == {
        "python",
        "py",
        "bash",
        "sh",
        "shell",
        "css",
        "toml",
    }


def test_prism_css_grammar_leaves_shimmer_dashes_uncolored() -> None:
    md = (DOCS_DIR / "utilities" / "shimmer.md").read_text(encoding="utf-8")
    match = re.search(r"```css\n([\s\S]*?)\n```", md)
    assert match is not None
    block = match.group(1)
    assertion = (
        f"const src = {json.dumps(block)};\n"
        "const out = global.Prism.highlight(src, global.Prism.languages.css, 'css');\n"
        "const operators = (out.match(/token operator/g) || []).length;\n"
        "const properties = (out.match(/token property/g) || []).length;\n"
        "const atrules = (out.match(/token atrule/g) || []).length;\n"
        "console.log(JSON.stringify({operators, properties, atrules}));\n"
    )
    payload = json.loads(_run_prism_js(assertion))
    assert payload["operators"] == 0
    assert payload["properties"] >= 30
    assert payload["atrules"] >= 10


def test_prism_bash_grammar_leaves_uv_command_dash_uncolored() -> None:
    assertion = (
        "const src = 'uv add buridan-ui';\n"
        "const out = global.Prism.highlight(src, global.Prism.languages.bash, 'bash');\n"
        "const operators = (out.match(/token operator/g) || []).length;\n"
        "console.log(JSON.stringify({operators, out}));\n"
    )
    payload = json.loads(_run_prism_js(assertion))
    assert payload["operators"] == 0
    assert "buridan-ui" in payload["out"]


def test_prism_bundle_preserves_python_grammar() -> None:
    assertion = (
        "const out = global.Prism.highlight('def f(): return 1', "
        "global.Prism.languages.python, 'python');\n"
        "const keywords = (out.match(/token keyword/g) || []).length;\n"
        "const numbers = (out.match(/token number/g) || []).length;\n"
        "console.log(JSON.stringify({keywords, numbers}));\n"
    )
    payload = json.loads(_run_prism_js(assertion))
    assert payload["keywords"] >= 2
    assert payload["numbers"] == 1


def test_prism_toml_grammar_tokenizes_pyproject_block() -> None:
    assertion = (
        "const src = '[tool.buridan]\\nname = \"x\"\\n';\n"
        "const out = global.Prism.highlight(src, global.Prism.languages.toml, 'toml');\n"
        "const tables = (out.match(/token table/g) || []).length;\n"
        "const keys = (out.match(/token key/g) || []).length;\n"
        "console.log(JSON.stringify({tables, keys}));\n"
    )
    payload = json.loads(_run_prism_js(assertion))
    assert payload["tables"] >= 1
    assert payload["keys"] >= 1


@pytest.mark.parametrize(
    "language", ["bash", "uv", "css", "assets/globals.css", "toml", "pyproject.toml"]
)
def test_render_pre_only_emits_bundled_prism_classes(language: str) -> None:
    resolved = _resolve_language_class(language)
    assert resolved in {
        "language-python",
        "language-bash",
        "language-css",
        "language-toml",
    }
