#!/usr/bin/env python3
"""Read-only Linear CLI built on the gtm-linear SDK.

The gtm-linear package (github.com/elviskahoro/sdk-python-linear) is a Python
SDK and deliberately ships no ``linear`` executable, so this thin wrapper
exposes its ``LinearWorkflow`` facade as shell commands for fetching Linear
issues from this workspace.

Auth: ``LINEAR_API_KEY`` (``lin_api_...``) resolved from the environment or a
``.env`` / ``.env.local`` file in the working directory — the same resolution
``LinearClient.from_env()`` performs. The workspace-root ``.env.local`` holds
the key and is gitignored.

Usage (from the workspace root; gtm-linear is a dev dependency, so ``uv run``
installs it automatically):

    uv run scripts/linear_cli.py viewer
    uv run scripts/linear_cli.py teams
    uv run scripts/linear_cli.py issues --team ENG [--state all] [--limit 25]
    uv run scripts/linear_cli.py issue ENG-123
    uv run scripts/linear_cli.py search "onboarding" [--limit 10]

Append ``--json`` to any command for machine-readable output. All commands are
read-only; for writes use the SDK directly (``gtm_linear.LinearMutations``).
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from pydantic import ValidationError

from gtm_linear import (
    LinearAPIError,
    LinearClient,
    LinearWorkflow,
    PaginationOrderBy,
)

# Linear's page-size ceiling for issue connections; larger --limit values are
# clamped rather than letting the API reject them.
MAX_PAGE_SIZE = 100

# Linear's numeric priority convention: 0 = no priority set. The API sends
# priorities as floats (2.0 == High), so normalize before the label lookup.
PRIORITY_LABELS = {1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}


def _workflow() -> LinearWorkflow:
    """Build a LinearWorkflow from env/dotenv auth, exiting with help on failure."""
    try:
        client = LinearClient.from_env()
    except ValidationError:
        sys.exit(
            "error: no LINEAR_API_KEY found. Set it in the environment or in a "
            ".env / .env.local file in the working directory (lin_api_... key).",
        )
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
        print(json.dumps([_issue_dict(i) for i in issues], indent=2))
        return

    if not issues:
        print("no issues found")
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
    header = "  ".join(header.ljust(widths[n]) for n, header in enumerate(columns))
    print(header)
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(cell.ljust(widths[n]) for n, cell in enumerate(row)))
    if verbose:
        for issue in issues:
            print(f"\n{issue.identifier}  {issue.url}")
            print(f"  description: {issue.description or '-'}")


def cmd_viewer(args: argparse.Namespace) -> int:
    """Auth check: print the user the API key belongs to."""
    with _workflow() as linear:
        user = linear.get_viewer()
    if args.json:
        print(json.dumps({"id": user.id, "name": user.name, "email": user.email}, indent=2))
    else:
        print(f"{user.name} <{user.email}>  (id: {user.id})")
    return 0


def cmd_teams(args: argparse.Namespace) -> int:
    """List teams. Not wrapped by the SDK, so this uses the raw GraphQL escape hatch."""
    with _workflow() as linear:
        data = linear.client.execute(
            "query { teams(first: 100) { nodes { id key name } } }",
        )
    nodes = data["teams"]["nodes"]
    if args.json:
        print(json.dumps(nodes, indent=2))
        return 0
    for team in nodes:
        print(f"{team['key']:<10} {team['name']}  (id: {team['id']})")
    return 0


def cmd_issues(args: argparse.Namespace) -> int:
    """List a team's issues, newest updated first (open ones by default)."""
    limit = min(args.limit, MAX_PAGE_SIZE)
    with _workflow() as linear:
        team = linear.get_team_by_key(args.team)
        if team is None:
            sys.exit(f"error: no Linear team with key {args.team!r}")
        if args.state == "open":
            issues = linear.list_open_team_issues(team.id, first=limit)
        else:
            page = linear.list_issues_page(
                {"team": {"id": {"eq": team.id}}},
                first=limit,
                order_by=PaginationOrderBy.updatedAt,
            )
            issues = list(page.nodes)
    _print_issues(issues, as_json=args.json, verbose=args.verbose)
    return 0


def cmd_issue(args: argparse.Namespace) -> int:
    """Fetch a single issue by its human identifier (e.g. ENG-123)."""
    identifier = args.identifier.upper()
    with _workflow() as linear:
        # get_issue() only accepts Linear UUIDs, so resolve the human identifier
        # through search and match on the exact identifier.
        result = linear.search_issues(identifier, first=25)
    match = next((i for i in result.nodes if i.identifier == identifier), None)
    if match is None:
        print(f"error: no issue found with identifier {identifier}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(_issue_dict(match), indent=2))
        return 0
    issue = match
    print(f"{issue.identifier}: {issue.title}")
    print(f"  url:      {issue.url}")
    print(f"  state:    {issue.state.name if issue.state else '-'}")
    print(f"  priority: {_priority_label(issue.priority)}")
    print(f"  assignee: {issue.assignee.name if issue.assignee else '-'}")
    print(f"  id:       {issue.id}")
    if issue.description:
        print("  description:")
        for line in issue.description.splitlines():
            print(f"    {line}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search issues across the workspace by free-text term."""
    limit = min(args.limit, MAX_PAGE_SIZE)
    with _workflow() as linear:
        result = linear.search_issues(args.term, first=limit)
    _print_issues(list(result.nodes), as_json=args.json, verbose=args.verbose)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linear_cli.py",
        description="Fetch Linear issues via the gtm-linear SDK (read-only).",
    )
    json_parent = argparse.ArgumentParser(add_help=False)
    json_parent.add_argument(
        "--json",
        action="store_true",
        help="emit JSON instead of a human-readable table",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    viewer = subparsers.add_parser(
        "viewer",
        help="who the LINEAR_API_KEY belongs to (auth check)",
        parents=[json_parent],
    )
    viewer.set_defaults(func=cmd_viewer)

    teams = subparsers.add_parser(
        "teams",
        help="list teams (key, name, id)",
        parents=[json_parent],
    )
    teams.set_defaults(func=cmd_teams)

    issues = subparsers.add_parser(
        "issues",
        help="list a team's issues, newest updated first",
        parents=[json_parent],
    )
    issues.add_argument("--team", required=True, help="team key, e.g. ENG")
    issues.add_argument(
        "--state",
        choices=("open", "all"),
        default="open",
        help="open (default) excludes completed and canceled issues",
    )
    issues.add_argument("--limit", type=int, default=25, help=f"max issues (default 25, cap {MAX_PAGE_SIZE})")
    issues.add_argument("-v", "--verbose", action="store_true", help="also print descriptions")
    issues.set_defaults(func=cmd_issues)

    issue = subparsers.add_parser(
        "issue",
        help="fetch one issue by identifier, e.g. ENG-123",
        parents=[json_parent],
    )
    issue.add_argument("identifier", help="issue identifier, e.g. ENG-123")
    issue.set_defaults(func=cmd_issue)

    search = subparsers.add_parser(
        "search",
        help="free-text issue search",
        parents=[json_parent],
    )
    search.add_argument("term", help="search term")
    search.add_argument("--limit", type=int, default=10, help=f"max results (default 10, cap {MAX_PAGE_SIZE})")
    search.add_argument("-v", "--verbose", action="store_true", help="also print descriptions")
    search.set_defaults(func=cmd_search)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except LinearAPIError as exc:
        print(f"Linear API error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
