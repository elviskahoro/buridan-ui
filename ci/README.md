# ci/

Dagger SDK program (plain Python, **no Dagger module/config**) holding the CI core logic. The same code runs locally and on RWX.

## Run locally
Needs Docker, `dagger` CLI **0.21.8**, and `uv`.

    ci/run.sh test        # pytest (node included in the container); results exported to ci-out/
    ci/run.sh validate    # generated docs/assets checks
    ci/run.sh pyright [paths]   # also pyrefly [paths]
    ci/run.sh all         # test + validate

Debug: `dagger run` prints the TUI/logs; set `CI_OUT_DIR` to change the export dir.

## Layers
- A (RWX, cached): uv, Dagger CLI (sha256-pinned), SDK venv (`ci/uv.lock`), engine image warm. None `use` the full checkout except via narrow `filter`s.
- B (RWX): triggers, status checks (`tests`, `docs-and-assets`), Captain retries, Trunk upload.
- C (Dagger): pytest run, asset validation, pyright/pyrefly.

Inside Dagger the layer order is: lockfiles -> `uv sync` (uv cache volume) -> source -> run, so source edits only re-run the last step.

## Expected cache behavior (RWX)
Docs-only / source edits invalidate only `pytest` / `validate` (both `cache: false`); `ci/uv.lock` changes rebuild `dagger-sdk-install`; root lockfile changes rebuild the Dagger deps layer.

## Notes
Dagger needs Docker: run it on RWX (`docker: true`), not in Conductor cloud sandboxes.
No RWX tool-cache/Dagger cache export yet; the Dagger engine cache is cold on each RWX run.
