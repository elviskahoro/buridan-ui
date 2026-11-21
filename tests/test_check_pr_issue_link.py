"""Tests for scripts/check-pr-issue-link.sh (PR issue-link check)."""

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check-pr-issue-link.sh"


def _run(body: str, author: str = "") -> int:
    env: dict[str, str] = {**os.environ, "PR_BODY": body, "PR_AUTHOR": author}
    return subprocess.run(  # noqa: S603
        [str(SCRIPT)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    ).returncode


@pytest.mark.parametrize(
    "body",
    [
        "Closes #12",
        "fixes #3 and more",
        "Resolves elviskahoro/buridan-ui#7",
        "Refs #9",
        "Part of #4",
        "No issue: release bump",
        "Why\n\nCloses #1\n",
    ],
)
def test_linked_passes(body: str) -> None:
    assert _run(body) == 0


@pytest.mark.parametrize(
    "body",
    ["", "no link here", "Closes #", "See #12 for context", "No issue:"],
)
def test_unlinked_fails(body: str) -> None:
    assert _run(body) == 1


def test_bot_skipped() -> None:
    assert _run("", "dependabot[bot]") == 0
