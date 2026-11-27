

# Pull requests always target this fork

This repository is a fork of `LineIndent/ui`. All PRs go to **this repo**
(`elviskahoro/buridan-ui`), base branch `main` — never to upstream
`LineIndent/ui`. Pass the repo explicitly so gh cannot misroute:

    gh pr create --repo elviskahoro/buridan-ui --base main

On 2026-10-15 a PR was routed to `LineIndent/ui` by mistake: gh prefers the
remote named `upstream` when no default repo is set. That remote was removed
from the Conductor clone — do not re-add it.

## Landing PRs

Agents merge PRs directly with `gh pr merge <pr-number> --squash` once every
required check is green and the user has said to merge. Do not offer to queue a
single PR.

The Trunk Merge Queue is only for landing a batch of PRs together, and only by
manual dispatch when the user asks for it.

- Submit (batch only): `trunk merge <pr-number>` (a number, not a URL or branch
  name).
- Check once: `trunk merge status <pr-number>`. States: Queued, Testing,
  Tests Passed, Merged. Report the state and stop. Never poll in a loop.
- Never use `--force`, `pause` or `resume`.
- Leave priority at the default (`medium`). `urgent` and `high` are for
  incidents and need an explicit reason from the user.
- Failed or PENDING_FAILURE: PENDING_FAILURE may be a flake, so retry once.
  Failed means push a fix to the PR branch and resubmit. Do not resubmit
  blindly in a loop.
- Auth failure: run `trunk login` once and retry.
- Refuse to queue from main or a protected branch.
- A `Closes #N` line in the PR body auto-closes the issue when the PR merges.
  Do not close the issue by hand beforehand.

The queue's required statuses live in `.trunk/trunk.yaml`
(`merge.required_statuses`) and must be live GitHub check names posted on
every PR. Re-verify after any pipeline rename:
`gh pr checks <pr-number> --json name --jq '.[].name'`. Do not add
path-filtered or `workflow_run`-triggered workflows there: they do not report
on every PR and would deadlock the queue.

Graph mode adds one more admission gate beyond `merge.required_statuses`: the
queue holds every PR at Not Ready until impacted targets have been uploaded
for its head sha. `.rwx/trunk-impacted-targets.yml` uploads them
on every PR to main (`PUT /v2/impacted-targets` authorized by
`TRUNK_API_KEY` from the `buridan-ui-trunk` RWX vault). The job stays out of
`merge.required_statuses` on purpose — the queue waits on the upload itself,
not the check — but a red `RWX: trunk-impacted-targets` status means nothing was
uploaded, and PRs stall at Not Ready even with every required status green.

The `upload` task is gated by PR author, so non-owner PRs (forks, Dependabot,
same-repo bots) skip it and post a green status without uploading — same
stall, all-green board. Recovery is folding the change into an
owner-authored PR: the gate keys on the PR author, which no push to the
stalled branch can change.

`pullfrog-approval` (Pullfrog's AI review verdict) is required on the GitHub
side only (ruleset `main - PR requirements` plus classic branch protection on
`main`, pinned to the Pullfrog app). It is deliberately not in
`merge.required_statuses`, so the Trunk queue does not wait on it.

<!-- entire-agent:begin -->
Read .entire/agent-guide.md for this repository's workflow, source inspection, and verification guidance.
@.entire/agent-guide.md
<!-- entire-agent:end -->

## PR descriptions

Use `.github/pull_request_template.md`. The full conventions are the
`create_pr` prompt in `.conductor/settings.toml`; see "Opening or editing a PR"
in `.entire/agent-guide.md`.

## PR issue links

PR bodies need `Closes #N`, `Refs #N` (partial work) or `No issue: <reason>`.
Bot PRs are skipped. The `check-pr-issue-link` RWX check enforces this.
