"""Tests for the Typer-based Linear CLI (scripts/linear_cli.py).

The SDK layer is mocked everywhere except the missing-key test, which
exercises the real pydantic-settings resolution against an empty directory
(no env var, no .env files).
"""

import json
import sys
import types
import unittest.mock as mock
from pathlib import Path

import pytest
from typer.testing import CliRunner

# ---------------------------------------------------------------------------
# Import the script under test — the repo root is not a package, and `scripts`
# is not part of the installed wheel, so put the root on sys.path explicitly.
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from gtm_linear import LinearAPIError, PaginationOrderBy  # noqa: E402
from scripts import linear_cli  # noqa: E402

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _issue(identifier: str = "EKK-1", title: str = "Test issue") -> types.SimpleNamespace:
    """A stand-in IssueFields object with the fields the CLI reads."""
    return types.SimpleNamespace(
        identifier=identifier,
        title=title,
        description=None,
        url=f"https://linear.app/me319/issue/{identifier}",
        state=types.SimpleNamespace(name="Backlog"),
        priority=2.0,
        assignee=None,
        id="issue-uuid",
    )


def _patch_workflow(inner: mock.MagicMock) -> mock._patch:
    """Patch ``linear_cli._workflow`` so its context yields ``inner``.

    ``__exit__`` must return False so exceptions raised inside the ``with``
    block (e.g. typer.Exit) propagate to the runner instead of being swallowed.
    """
    workflow = mock.MagicMock()
    workflow.__enter__.return_value = inner
    workflow.__exit__.return_value = False
    return mock.patch.object(linear_cli, "_workflow", return_value=workflow)


def _team() -> types.SimpleNamespace:
    return types.SimpleNamespace(id="team-uuid", key="EKK", name="Elvis")


def _all_output(result) -> str:
    """stdout plus stderr, tolerating click versions that mix or split them."""
    try:
        return result.output + result.stderr
    except ValueError:
        return result.output


# ---------------------------------------------------------------------------
# Issues listing
# ---------------------------------------------------------------------------


def test_issues_default_state_open_uses_open_helper() -> None:
    inner = mock.MagicMock()
    inner.get_team_by_key.return_value = _team()
    inner.list_open_team_issues.return_value = [_issue()]

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["issues", "--team", "EKK"])

    assert result.exit_code == 0
    inner.list_open_team_issues.assert_called_once_with("team-uuid", first=25)
    inner.list_issues_page.assert_not_called()
    assert "EKK-1" in result.output


def test_issues_state_all_uses_filtered_page() -> None:
    inner = mock.MagicMock()
    inner.get_team_by_key.return_value = _team()
    inner.list_issues_page.return_value = types.SimpleNamespace(nodes=[_issue()])

    with _patch_workflow(inner):
        result = runner.invoke(
            linear_cli.app,
            ["issues", "--team", "EKK", "--state", "all"],
        )

    assert result.exit_code == 0
    inner.list_open_team_issues.assert_not_called()
    args, kwargs = inner.list_issues_page.call_args
    assert args[0] == {"team": {"id": {"eq": "team-uuid"}}}
    assert kwargs.get("order_by") is PaginationOrderBy.updatedAt
    assert "EKK-1" in result.output


def test_issues_json_output_parses() -> None:
    inner = mock.MagicMock()
    inner.get_team_by_key.return_value = _team()
    inner.list_open_team_issues.return_value = [_issue()]

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["issues", "--team", "EKK", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload[0]["identifier"] == "EKK-1"
    assert payload[0]["state"] == "Backlog"


def test_unknown_team_exits_1() -> None:
    inner = mock.MagicMock()
    inner.get_team_by_key.return_value = None

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["issues", "--team", "NOPE"])

    assert result.exit_code == 1
    assert "no Linear team" in _all_output(result)


@pytest.mark.parametrize("bad_limit", ["0", "-5", "500"])
def test_out_of_range_limit_is_a_usage_error(bad_limit: str) -> None:
    result = runner.invoke(
        linear_cli.app,
        ["issues", "--team", "EKK", "--limit", bad_limit],
    )
    assert result.exit_code == 2


# ---------------------------------------------------------------------------
# Single issue and search
# ---------------------------------------------------------------------------


def test_issue_found_prints_details_and_uppercases_identifier() -> None:
    inner = mock.MagicMock()
    inner.search_issues.return_value = types.SimpleNamespace(nodes=[_issue()])

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["issue", "ekk-1"])

    assert result.exit_code == 0
    inner.search_issues.assert_called_once_with("EKK-1", first=25)
    assert "EKK-1: Test issue" in result.output


def test_issue_not_found_exits_1() -> None:
    inner = mock.MagicMock()
    inner.search_issues.return_value = types.SimpleNamespace(nodes=[])

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["issue", "EKK-999"])

    assert result.exit_code == 1
    assert "no issue found" in _all_output(result)


# ---------------------------------------------------------------------------
# Auth and error mapping
# ---------------------------------------------------------------------------


def test_missing_api_key_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)  # no .env / .env.local here

    result = runner.invoke(linear_cli.app, ["viewer"])

    assert result.exit_code == 1
    assert "no LINEAR_API_KEY" in _all_output(result)


def test_main_maps_linear_api_error_to_system_exit_1() -> None:
    with mock.patch.object(linear_cli, "app", side_effect=LinearAPIError("boom")):
        with pytest.raises(SystemExit) as excinfo:
            linear_cli.main()

    assert excinfo.value.code == 1


def test_linear_api_error_from_command_exits_1() -> None:
    inner = mock.MagicMock()
    inner.get_viewer.side_effect = LinearAPIError("boom")

    with _patch_workflow(inner):
        result = runner.invoke(linear_cli.app, ["viewer"])

    assert result.exit_code == 1
    assert isinstance(result.exception, LinearAPIError)
