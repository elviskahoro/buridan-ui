

# Pull requests always target this fork

This repository is a fork of `LineIndent/ui`. All PRs go to **this repo**
(`elviskahoro/buridan-ui`), base branch `main` — never to upstream
`LineIndent/ui`. Pass the repo explicitly so gh cannot misroute:

    gh pr create --repo elviskahoro/buridan-ui --base main

On 2026-10-15 a PR was routed to `LineIndent/ui` by mistake: gh prefers the
remote named `upstream` when no default repo is set. That remote was removed
from the Conductor clone — do not re-add it.

<!-- entire-agent:begin -->
Read .entire/agent-guide.md for this repository's workflow, source inspection, and verification guidance.
@.entire/agent-guide.md
<!-- entire-agent:end -->
