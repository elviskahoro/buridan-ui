#!/usr/bin/env python3
"""Read-only Linear CLI built on the gtm-linear SDK, powered by Typer.

The gtm-linear package (github.com/elviskahoro/sdk-python-linear) is a Python
SDK and deliberately ships no ``linear`` executable, so this thin wrapper
exposes its ``LinearWorkflow`` facade as shell commands for fetching Linear
issues from this workspace.

Auth: ``LINEAR_API_KEY`` (``lin_api_...``) resolved from the environment or a
``.env`` / ``.env.local`` file in the working directory — the same resolution
``LinearClient.from_env()`` performs. The workspace-root ``.env.local`` holds
the key and is gitignored.

Usage (from the workspace root; gtm-linear and typer are dev dependencies, so
``uv run`` installs them automatically):

    uv run scripts/linear_cli.py viewer
    uv run scripts/linear_cli.py teams
    uv run scripts/linear_cli.py issues --team ENG [--state all] [--limit 25]
    uv run scripts/linear_cli.py issue ENG-123
    uv run scripts/linear_cli.py search "onboarding" [--limit 10]

Append ``--json`` to any command for machine-readable output. All commands are
read-only; for writes use the SDK directly (``gtm_linear.LinearMutations``).
"""

from __future__ import annotations

import enum
import json
from typing import Any

import typer
from pydantic import ValidationError

from gtm_linear import (
    LinearAPIError,
    LinearClient,
    LinearWorkflow,
    PaginationOrderBy,
)

app = typer.Typer(
    help="Fetch Linear issues via the gtm-linear SDK (read-only).",
    no_args_is_help=True,
)

# Linear's page-size ceiling for issue connections; larger --limit values are
# clamped rather than letting the API reject them.
MAX_PAGE_SIZE = 100

# Linear's numeric priority convention: 0 = no priority set. The API sends
# priorities as floats (2.0 == High), so normalize before the label lookup.
PRIORITY_LABELS = {1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}


class State(enum.Enum):
    """Which issues a team listing includes."""

    open = "open"
    all = "all"


# --- helpers (logic kept separate from the thin Typer command functions) ---


def _workflow() -> LinearWorkflow:
    """Build a LinearWorkflow from env/dotenv auth, exiting with help on failure."""
    try:
        client = LinearClient.from_env()
    except ValidationError:
        typer.secho(
            "error: no LINEAR_API_KEY found. Set it in the environment or in a "
            ".env / .env.local file in the working directory (lin_api_... key).",
            err=True,
        )
        raise typer.Exit(code=1) from None
    return LinearWorkflow(client.api_key)


def _issue_dict(issue: Any) -> dict[str, Any]:
    """Flatten one issue into the dict shape used by --json output."""
    return {
        "identifier": issue.identifier,
        "title": issue.title,
        "description": issue.description,
        "url": issue.url,
        "state": issue.state.name if issue.state else None,
        "priority": issue.priority,
        "assignee": issue.assignee.name if issue.assignee else None,
        "id": issue.id,
    }


def _priority_label(priority: float | None) -> str:
    if priority is None:
        return "-"
    level = int(priority)
    if level == 0:
        return "-"
    return PRIORITY_LABELS.get(level, str(level))


def _print_issues(issues: list[Any], *, as_json: bool, verbose: bool = False) -> None:
    """Render an issue list as JSON or an aligned table."""
    if as_json:
        typer.echo(json.dumps([_issue_dict(i) for i in issues], indent=2))
        return

    if not issues:
        typer.echo("no issues found")
        return

    columns = ("IDENTIFIER", "STATE", "PRIORITY", "ASSIGNEE", "TITLE")
    rows = [
        (
            i.identifier,
            i.state.name if i.state else "-",
            _priority_label(i.priority),
            i.assignee.name if i.assignee else "-",
            i.title,
        )
        for i in issues
    ]
    widths = [
        max(len(header), *(len(row[n]) for row in rows)) if rows else len(header)
        for n, header in enumerate(columns)
    ]
    typer.echo("  ".join(header.ljust(widths[n]) for n, header in enumerate(columns)))
    typer.echo("  ".join("-" * w for w in widths))
    for row in rows:
        typer.echo("  ".join(cell.ljust(widths[n]) for n, cell in enumerate(row)))
    if verbose:
        for issue in issues:
            typer.echo(f"\n{issue.identifier}  {issue.url}")
            typer.echo(f"  description: {issue.description or '-'}")


# --- commands ---


@app.command()
def viewer(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON instead of human-readable output.",
    ),
) -> None:
    """Auth check: print the user the API key belongs to."""
    with _workflow() as linear:
        user = linear.get_viewer()
    if as_json:
        typer.echo(
            json.dumps({"id": user.id, "name": user.name, "email": user.email}, indent=2),
        )
    else:
        typer.echo(f"{user.name} <{user.email}>  (id: {user.id})")


@app.command()
def teams(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON instead of human-readable output.",
    ),
) -> None:
    """List teams (key, name, id)."""
    # Not wrapped by the SDK, so this uses the raw GraphQL escape hatch.
    with _workflow() as linear:
        data = linear.client.execute(
            "query { teams(first: 100) { nodes { id key name } } }",
        )
    nodes = data["teams"]["nodes"]
    if as_json:
        typer.echo(json.dumps(nodes, indent=2))
        return
    for team in nodes:
        typer.echo(f"{team['key']:<10} {team['name']}  (id: {team['id']})")


@app.command()
def issues(
    team: str = typer.Option(..., help="Team key, e.g. ENG."),
    state: State = typer.Option(
        State.open,
        help="Open (default) excludes completed and canceled issues.",
    ),
    limit: int = typer.Option(
        25,
        help=f"Max issues to fetch (default 25, capped at {MAX_PAGE_SIZE}).",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Also print descriptions."),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON instead of human-readable output.",
    ),
) -> None:
    """List a team's issues, newest updated first."""
    limit = min(limit, MAX_PAGE_SIZE)
    with _workflow() as linear:
        resolved = linear.get_team_by_key(team)
        if resolved is None:
            typer.secho(f"error: no Linear team with key {team!r}", err=True)
            raise typer.Exit(code=1)
        if state is State.open:
            fetched = linear.list_open_team_issues(resolved.id, first=limit)
        else:
            page = linear.list_issues_page(
                {"team": {"id": {"eq": resolved.id}}},
                first=limit,
                order_by=PaginationOrderBy.updatedAt,
            )
            fetched = list(page.nodes)
    _print_issues(fetched, as_json=as_json, verbose=verbose)


@app.command()
def issue(
    identifier: str = typer.Argument(help="Issue identifier, e.g. ENG-123."),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON instead of human-readable output.",
    ),
) -> None:
    """Fetch one issue by its human identifier."""
    identifier = identifier.upper()
    with _workflow() as linear:
        # get_issue() only accepts Linear UUIDs, so resolve the human identifier
        # through search and match on the exact identifier.
        result = linear.search_issues(identifier, first=25)
    match = next((i for i in result.nodes if i.identifier == identifier), None)
    if match is None:
        typer.secho(f"error: no issue found with identifier {identifier}", err=True)
        raise typer.Exit(code=1)
    if as_json:
        typer.echo(json.dumps(_issue_dict(match), indent=2))
        return
    typer.echo(f"{match.identifier}: {match.title}")
    typer.echo(f"  url:      {match.url}")
    typer.echo(f"  state:    {match.state.name if match.state else '-'}")
    typer.echo(f"  priority: {_priority_label(match.priority)}")
    typer.echo(f"  assignee: {match.assignee.name if match.assignee else '-'}")
    typer.echo(f"  id:       {match.id}")
    if match.description:
        typer.echo("  description:")
        for line in match.description.splitlines():
            typer.echo(f"    {line}")


@app.command()
def search(
    term: str = typer.Argument(help="Search term."),
    limit: int = typer.Option(
        10,
        help=f"Max results (default 10, capped at {MAX_PAGE_SIZE}).",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Also print descriptions."),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON instead of human-readable output.",
    ),
) -> None:
    """Free-text issue search across the workspace."""
    limit = min(limit, MAX_PAGE_SIZE)
    with _workflow() as linear:
        result = linear.search_issues(term, first=limit)
    _print_issues(list(result.nodes), as_json=as_json, verbose=verbose)


def main() -> None:
    """Entry point: run the Typer app, mapping SDK errors to a clean exit."""
    try:
        app()
    except LinearAPIError as exc:
        typer.secho(f"Linear API error: {exc}", fg=typer.colors.RED, err=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
