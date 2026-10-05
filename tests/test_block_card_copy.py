"""Regression tests for the command-copy button rendered by ``block_card``."""

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.examples import utils as example_utils  # noqa: E402

SAMPLE_COMMAND = "uv run buridan add sample_block"


@example_utils.block_card
def sample_block():
    return example_utils.rx.el.div("content")


def _find_button(component: Any) -> Any:
    if getattr(component, "tag", None) == "button":
        return component

    for child in getattr(component, "children", []):
        button = _find_button(child)
        if button is not None:
            return button

    return None


def test_block_card_keeps_terminal_icon_separate_from_command_text() -> None:
    button = _find_button(sample_block())

    assert button is not None
    assert len(button.children) == 2

    icon, command_text = button.children
    assert "TerminalIcon" in str(icon.icon)
    assert getattr(command_text, "tag", None) == "span"
    assert json.loads(str(command_text.children[0])) == SAMPLE_COMMAND
    assert command_text.id == f"text-{button.id}"


def test_block_card_copy_feedback_targets_only_command_text_span(monkeypatch) -> None:
    scripts = []
    call_script = example_utils.rx.call_script

    def capture_script(script: str):
        scripts.append(script)
        return call_script(script)

    monkeypatch.setattr(example_utils.rx, "call_script", capture_script)
    button = _find_button(sample_block())

    assert button is not None
    assert len(scripts) == 1
    script = scripts[0]
    text_id = f"text-{button.id}"

    text_variable_match = re.search(
        rf"\b(?:const|let|var)\s+([\w$]+)\s*=\s*document\s*\.\s*"
        rf"getElementById\s*\(\s*['\"]{re.escape(text_id)}['\"]\s*\)",
        script,
    )
    assert text_variable_match is not None
    text_variable = re.escape(text_variable_match.group(1))

    original_variable_match = re.search(
        rf"\b(?:const|let|var)\s+([\w$]+)\s*=\s*{text_variable}\s*\.\s*innerText\b",
        script,
    )
    assert original_variable_match is not None
    original_variable = re.escape(original_variable_match.group(1))

    assert re.search(
        rf"navigator\s*\.\s*clipboard\s*\.\s*writeText\s*\(\s*"
        rf"(['\"]){re.escape(SAMPLE_COMMAND)}\1\s*\)",
        script,
    )
    assert re.search(
        rf"\b{text_variable}\s*\.\s*innerText\s*=\s*(['\"])Copied!\1", script
    )
    assert re.search(
        rf"\b{text_variable}\s*\.\s*innerText\s*=\s*{original_variable}\b",
        script,
    )

    inner_text_targets = re.findall(r"\b([\w$]+)\s*\.\s*innerText\s*=", script)
    assert len(inner_text_targets) == 2
    assert set(inner_text_targets) == {text_variable_match.group(1)}
