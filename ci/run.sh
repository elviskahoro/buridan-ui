#!/usr/bin/env bash
# Run a CI check locally or on RWX: ci/run.sh <test|validate|pyright|pyrefly|all> [args]
# Needs Docker and the `dagger` CLI (0.21.8). Python deps come from ci/pyproject.toml via uv.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${CI_PYTHON:-}" ]]; then
	exec dagger run "${CI_PYTHON}" ci/main.py "$@"
fi
exec dagger run uv run --project ci python ci/main.py "$@"
