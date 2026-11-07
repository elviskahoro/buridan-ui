---
name: rwx
description: Run RWX CI pipelines and read logs from the CLI using the injected RWX access tokens, including runs that include the current working directory's uncommitted git changes. Use when asked to run CI/tests on RWX, debug a failing RWX check, or fetch RWX logs.
---

# RWX CLI in this repo

CI definitions live in `.rwx/` (`tests.yml`, `trunk-check.yml`, `validate-assets.yml`, `trunk-impacted-targets.yml`, `pyright.yml`, `pyrefly.yml`). Each has an `on.cli` trigger, so it can be started locally.

## Auth: two injected tokens, one per RWX workspace

Two env vars are injected into the environment, named `RWX_ACCESS_TOKEN_<SUFFIX>`. Each token is scoped to one RWX workspace. List the names without values:

```bash
env | grep -E '^RW[XC]_ACCESS_TOKEN_' | cut -d= -f1
```

The `<SUFFIX>` is the workspace name, uppercased. The prefix may be `RWC_` instead of `RWX_` (e.g. `RWC_ACCESS_TOKEN_ELVISKAHORO`); match on the suffix. The token for this repo is the one whose suffix matches the repo owner (the owner in the `git remote` URL, e.g. `github.com/<owner>/buridan-ui`, uppercased). Use the other token only for runs in the other workspace.

The CLI reads only `RWX_ACCESS_TOKEN` (or `--access-token`), so export the matching token under that name. Do this per command and never print the token:

```bash
OWNER=$(git remote get-url origin | sed -E 's#.*[:/]([^/]+)/[^/]+(\.git)?$#\1#' | tr a-z A-Z)
export RWX_ACCESS_TOKEN="$(printenv "RWX_ACCESS_TOKEN_$OWNER" || printenv "RWC_ACCESS_TOKEN_$OWNER")"
# or, one-off:
rwx runs list --access-token "$RWX_ACCESS_TOKEN"
```

A run, task, or log ID only resolves under the workspace that owns it. If a lookup returns not-found or unauthorized, switch tokens.

## Running a pipeline with your current git changes

`rwx run` sends a git patch with the run, so no commit or push is needed:

- Base: the closest ancestor of local `HEAD` that is already on `origin`. `event.git.sha` resolves to it.
- Patch on top: unpushed local commits, staged changes, unstaged changes, and untracked files.
- Excluded: anything in `.gitignore`. Git LFS changes error out; commit and push those first.
- `RWX_DISABLE_GIT_PATCH=1` turns patching off.

```bash
rwx run .rwx/tests.yml --wait --fail-fast          # run CI on the working tree, wait for result
rwx run .rwx/tests.yml --target <task-key> --wait  # only one task (and its dependencies)
rwx run .rwx/tests.yml --title "wip: my change" --json
```

The `git/clone` task takes `ref: ${{ init.commit-sha }}`, and the `cli` trigger sets `commit-sha: ${{ event.git.sha }}`. That wiring is what makes the patch apply, so keep it when editing `.rwx/*.yml`. Edits to the `.rwx` files themselves are also picked up locally.

## Type checking without a local `.venv`

`pyright.yml` and `pyrefly.yml` run the checkers with a synced venv on your working tree (uncommitted, untracked and unpushed commits included). Use them instead of retrying locally when there is no `.venv` or memory is tight. They are manual only: no PR or push trigger.

```bash
rwx run .rwx/pyright.yml --wait                                  # whole project
rwx run .rwx/pyright.yml --wait --init paths="app/foo.py app/bar.py"   # specific files
rwx run .rwx/pyrefly.yml --wait --init paths="app/foo.py"
```

A failed run prints the failing task id; read the errors with `rwx logs <task-id>`.

## Logs and results

```bash
rwx runs list
rwx results <run-id>                          # status and failures for a run
rwx logs <task-id>                            # download logs for a task
rwx logs <run-id> --task <task-key> --output /tmp/logs
```

`rwx run` prints the run URL and ID. Use `--json` for parsing.

## Docs

`rwx docs search "<query>"` and `rwx docs pull /docs/cli-triggers` (also `/docs/cli-reference/rwx-run`).
