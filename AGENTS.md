

# Pull requests always target this fork

This repository is a fork of `LineIndent/ui`. All PRs go to **this repo**
(`elviskahoro/buridan-ui`), base branch `main` — never to upstream
`LineIndent/ui`. Pass the repo explicitly so gh cannot misroute:

    gh pr create --repo elviskahoro/buridan-ui --base main

On 2026-10-15 a PR was routed to `LineIndent/ui` by mistake: gh prefers the
remote named `upstream` when no default repo is set. That remote was removed
from the Conductor clone — do not re-add it.

## Landing PRs

PRs land through the Trunk Merge Queue, not the GitHub Merge button.

- Submit: `trunk merge <pr-number>` (a number, not a URL or branch name).
- Check once: `trunk merge status <pr-number>`. States: Queued, Testing,
  Tests Passed, Merged. Report the state and stop. Never poll in a loop.
- Never use `gh pr merge` or the GitHub Merge button. They bypass the queue.
- Never use `--force`, `pause` or `resume`.
- Leave priority at the default (`medium`). `urgent` and `high` are for
  incidents and need an explicit reason from the user.
- Failed or PENDING_FAILURE: PENDING_FAILURE may be a flake, so retry once.
  Failed means push a fix to the PR branch and resubmit. Do not resubmit
  blindly in a loop.
- Auth failure: run `trunk login` once and retry.
- Refuse to queue from main or a protected branch.
- A `Closes #N` line in the PR body auto-closes the issue when the queue lands
  the PR. Do not close the issue by hand beforehand.

Because the queue auto-merges once its predictive CI passes, the user's "yes"
on the final PR preview is the explicit human authorization to merge — after
it, submit with `trunk merge <pr-number>` without re-prompting. There is no
second gate before the merge lands.

The queue's required statuses live in `.trunk/trunk.yaml`
(`merge.required_statuses`) and must be live GitHub check names posted on
every PR. Re-verify after any pipeline rename:
`gh pr checks <pr-number> --json name --jq '.[].name'`. Do not add
path-filtered or `workflow_run`-triggered workflows there: they do not report
on every PR and would deadlock the queue.

`pullfrog-approval` (AI review verdict) is required in both layers: on the
GitHub side (ruleset `main - PR requirements` plus classic branch protection
on `main`, pinned to the Pullfrog app — gates direct merges and queue
admission) and in `merge.required_statuses`, so the queue waits for a fresh
Pullfrog verdict on the exact merge state it tests. This relies on the queue
testing in draft-PR mode with pullfrog reviewing the trunk-io draft PRs
(`review.drafts` on; trunk-io is not in pullfrog's bot-exclusion list). If a
queue entry stalls on a missing `pullfrog-approval`, check those two things
and whether the pullfrog run failed or was cancelled before changing the
list.

<!-- entire-agent:begin -->
Read .entire/agent-guide.md for this repository's workflow, source inspection, and verification guidance.
@.entire/agent-guide.md
<!-- entire-agent:end -->
