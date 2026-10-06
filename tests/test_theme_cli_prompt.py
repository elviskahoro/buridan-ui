"""Regression tests for the export-dialog Copy button rendered by ``theme_cli_prompt``.

The "Get Code" export dialog in ``app/templates/compiler.py:theme_cli_prompt``
has two surfaces that must agree in its default Local mode:

* the visible ``<code>`` block (what the user reads), and
* the ``rx.set_clipboard`` payload on the Copy button (what the user pastes).

Commit ``755f3ed`` corrected only the visible block to
``uv run buridan apply --preset {seed}``; the clipboard branch stayed on the
stale ``uv run buridan init --preset {seed} --include {preset}`` (rejected by
the CLI since ``8dc954cf``).  These tests pin both surfaces to the real
``apply --preset`` command and guard against the one-sided-edit footgun that
caused the display/clipboard divergence.
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.templates.compiler import theme_cli_prompt

# Literal prefixes — the unique discriminator between the buggy and fixed
# local-mode clipboard payload.  ``uv run buridan init --preset `` only ever
# appeared in the stale local clipboard branch (the online branch prefixes its
# ``init`` with ``pip install buridan-create and buridan init --preset ``).
FIXED_LOCAL_PREFIX = "uv run buridan apply --preset "
BUGGY_LOCAL_PREFIX = "uv run buridan init --preset "

# State-var reference names used in the compiled JS (see app/hooks.py).
SEED_REF = "_client_state_dict_seed"
PRESET_OPTION_REF = "_client_state_dict_theme_preset_option"


# ---------------------------------------------------------------------------
# Tree-walking helpers
# ---------------------------------------------------------------------------


def _find_by_tag(component, tag):
    found = []
    if getattr(component, "tag", None) == tag:
        found.append(component)
    for child in getattr(component, "children", []) or []:
        found.extend(_find_by_tag(child, tag))
    return found


def _clipboard_event_expr(button) -> str:
    """Compiled JS for the ``rx.set_clipboard`` on_click event of ``button``."""
    events = button.event_triggers["on_click"].events
    for event in events:
        for arg_pair in event.args:
            inner = arg_pair[1]
            expr = getattr(inner, "_js_expr", None)
            if expr and "clipboard" in expr and "writeText" in expr:
                return expr
    raise AssertionError("Copy button has no navigator.clipboard.writeText event")


def _ternary_branches(expr: str):
    """Return ``(if_true, if_false)`` substrings of the top-level ``?:`` ternary.

    The compiled Reflex ternary takes the form ``((cond) ? (local) : (online))``.
    The condition uses optional chaining (``?.``) rather than a ternary ``?:``,
    so the first ``? (`` sequence unambiguously marks the ternary.
    """
    match = re.search(r"\?\s*\((.*?)\)\s*:\s*\(", expr)
    assert match is not None, f"no top-level ternary in: {expr!r}"
    if_true = match.group(1)
    if_false = expr[match.end() :]
    return if_true, if_false


# ---------------------------------------------------------------------------
# Clipboard payload
# ---------------------------------------------------------------------------


def test_copy_button_local_branch_uses_apply_not_init() -> None:
    button = _find_by_tag(theme_cli_prompt(), "button")[0]
    expr = _clipboard_event_expr(button)

    local_branch, _ = _ternary_branches(expr)

    assert FIXED_LOCAL_PREFIX in local_branch
    assert BUGGY_LOCAL_PREFIX not in local_branch
    assert " --include " not in local_branch
    assert PRESET_OPTION_REF not in local_branch
    assert SEED_REF in local_branch


# ---------------------------------------------------------------------------
# Displayed <code> block
# ---------------------------------------------------------------------------


def test_displayed_code_block_local_branch_uses_apply_command() -> None:
    code = _find_by_tag(theme_cli_prompt(), "code")[0]
    displayed = str(code.children[0])

    local_branch, _ = _ternary_branches(displayed)

    assert FIXED_LOCAL_PREFIX in local_branch
    assert BUGGY_LOCAL_PREFIX not in local_branch
    assert " --include " not in local_branch


# ---------------------------------------------------------------------------
# Display / clipboard parity
# ---------------------------------------------------------------------------


def test_clipboard_local_branch_matches_displayed_block() -> None:
    button = _find_by_tag(theme_cli_prompt(), "button")[0]
    code = _find_by_tag(theme_cli_prompt(), "code")[0]

    clipboard_local, _ = _ternary_branches(_clipboard_event_expr(button))
    displayed_local, _ = _ternary_branches(str(code.children[0]))

    assert clipboard_local == displayed_local
