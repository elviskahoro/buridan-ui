# noqa: INP001
"""Regression guards for the markdown code-block renderer in ``render_pre``.

``render_pre`` (the ``"pre"`` entry of ``markdown_component_map``) renders every
markdown code fence on the docs pages. The vendored Prism bundle auto-runs
``Prism.highlightAll()`` exactly once at first page load (DOMContentLoaded /
rAF); after a client-side route change the newly mounted ``<pre><code>`` blocks
are mounted after that one-shot highlight has already fired, so they render as
plain untokenized text unless something re-triggers highlighting on mount.

The sibling wrappers in ``app/www/wrapper.py`` (``demo_wrapper``,
``chart_util_wrapper``) already attach ``on_mount=rx.call_script("Prism.highlightAll()")``
to their ``<code>`` element, which re-highlights the page on mount. The
markdown path historically lacked this trigger, so docs pages reached via
in-app navigation (e.g. the getting-started pages that render no demo/chart
wrapper) showed unstyled code -- and the compiled bundle contained exactly one
``Prism.highlightAll`` occurrence (the wrapper's).

These tests pin the contract that:

* ``render_pre``'s ``<code>`` element carries an ``on_mount`` EventChain that
  runs ``Prism.highlightAll()`` (the in-memory Reflex tree surface).
* The compiled ``ComponentMap`` wrapper that ships in the client bundle emits a
  ``useEffect`` calling ``Prism.highlightAll()`` (the surface the bug report
  searched the built bundle for -- mirroring that exact method here).
* ``render_pre`` shares the same ``on_mount`` contract as the demo/chart
  wrappers, eliminating the codebase inconsistency.
"""

import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx  # noqa: E402

from app.www import wrapper  # noqa: E402
from app.www.style import markdown_component_map, render_pre  # noqa: E402

PRISM_CALL = "Prism.highlightAll()"


def _find_codes(component: Any, found: list[Any] | None = None) -> list[Any]:  # noqa: ANN401
    """Recursively collect every ``<code>`` element in the component tree."""
    if found is None:
        found = []
    if getattr(component, "tag", None) == "code":
        found.append(component)
    for child in getattr(component, "children", []) or []:
        _find_codes(child, found)
    return found


def _first_code(component: Any) -> Any:  # noqa: ANN401
    """Return the first ``<code>`` element in the tree, asserting it exists."""
    codes = _find_codes(component)
    assert codes, "expected at least one <code> element in the rendered tree"
    return codes[0]


def _on_mount_script(component: Any) -> str:  # noqa: ANN401
    """Return the literal JS string of the ``on_mount`` call, asserting one exists.

    The wrapper pattern attaches ``on_mount=rx.call_script("Prism.highlightAll()")``,
    which compiles to a single-event ``EventChain`` whose ``EventSpec.args`` embed
    a ``LiteralStringVar`` whose ``_var_value`` is the JS source. Asserting on
    ``str(event.args)`` keeps the test robust against Reflex renaming the var
    plumbing while still pinning the shipped script body.
    """
    assert "on_mount" in component.event_triggers, (
        "<code> element is missing the on_mount event trigger; Prism is never "
        "re-invoked after client-side navigation, so markdown code fences render "
        "as plain untokenized text on docs pages reached via in-app navigation."
    )
    on_mount = component.event_triggers["on_mount"]
    events = list(getattr(on_mount, "events", []) or [])
    assert len(events) == 1, f"expected exactly one on_mount event, got {len(events)}"
    return str(events[0].args)


def test_render_pre_code_element_re_invokes_prism_on_mount() -> None:
    """``render_pre``'s ``<code>`` mounts ``Prism.highlightAll()``.

    This is the in-memory Reflex-tree surface of the fix: the ``<code>`` element
    produced by ``render_pre`` carries an ``on_mount`` ``EventChain`` whose
    event args embed the literal ``Prism.highlightAll()`` script, matching the
    established ``app/www/wrapper.py`` pattern. Without this trigger, the
    vendored Prism bundle's one-shot DOMContentLoaded highlight is the only
    highlight that ever fires, so code fences mounted by client-side
    navigation are never tokenized.
    """
    code = _first_code(render_pre("x = 1\ny = 2", language="python"))

    assert str(code.class_name) == "language-python"
    assert PRISM_CALL in _on_mount_script(code)


def test_render_pre_on_mount_trigger_survives_markdown_compilation() -> None:
    """The shipped ``ComponentMap`` wrapper emits a ``useEffect`` for Prism.

    Reflex hoists every component-map renderer's ``on_mount`` hooks into a
    single ``ComponentMap_<hash>`` React function that ships in the client
    bundle. The bug report established the defect by searching the built
    bundle for ``Prism.highlightAll`` and finding exactly one occurrence
    (the wrapper's). This test mirrors that investigative check against the
    same compiled output (``Markdown._get_custom_code``), asserting the
    markdown path now contributes its own ``useEffect`` calling
    ``Prism.highlightAll()`` -- so the shipped docs route chunk re-highlights
    on every Markdown mount.
    """
    markdown = rx.markdown(
        "```python\nx = 1\n```\n",
        component_map=markdown_component_map,
    )
    # ``_get_custom_code`` emits the ``ComponentMap_<hash>`` React function that
    # ships in the client bundle (with all hoisted ``on_mount`` hooks). It is a
    # Reflex-internal compiler hook with no public alias, so access it directly
    # -- this mirrors the bug report's method of searching the built bundle.
    compiled = str(
        markdown.children[0]._get_custom_code(),  # noqa: SLF001  # pyright: ignore[reportAttributeAccessIssue]  # pyrefly: ignore[missing-attribute]
    )

    assert "useEffect" in compiled, (
        "expected the ComponentMap wrapper to ship a useEffect hook"
    )
    assert PRISM_CALL in compiled, (
        "expected the shipped ComponentMap wrapper to call Prism.highlightAll() "
        "from a useEffect; without it, client-side navigation never re-highlights "
        "markdown code fences"
    )


def test_render_pre_shares_prism_on_mount_contract_with_wrappers() -> None:
    """``render_pre`` and the demo/chart wrappers share one mount contract.

    The bug report called out a codebase inconsistency: ``demo_wrapper`` and
    ``chart_util_wrapper`` explicitly re-trigger Prism on mount (which
    incidentally re-highlights the page's other code blocks), while
    ``render_pre`` lacked it. Both call sites must use the same hook so docs
    pages without a demo/chart wrapper are not silently left unhighlighted.
    """
    render_pre_code = _first_code(render_pre("x = 1", language="python"))
    demo_code = _first_code(wrapper.demo_wrapper(rx.el.div("hi"), source="print(1)"))
    chart_code = _first_code(wrapper.chart_util_wrapper(source="print(1)"))

    assert PRISM_CALL in _on_mount_script(render_pre_code)
    assert PRISM_CALL in _on_mount_script(demo_code)
    assert PRISM_CALL in _on_mount_script(chart_code)
