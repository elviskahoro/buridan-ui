"""Dagger SDK program for buridan-ui CI. Plain program, no Dagger module.

Usage: dagger run python ci/main.py <test|validate|pyright|pyrefly|all> [args]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import dagger
from dagger import dag

REPO = Path(__file__).resolve().parent.parent
PYTHON_IMAGE = "python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535"
NODE_IMAGE = "node:22.23.4-slim@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d"
UV_VERSION = "0.11.29"
PYRIGHT_VERSION = "1.1.414"
PYREFLY_VERSION = "1.3.1"
APP = "/app"
EXCLUDE = [
    ".git",
    ".venv",
    "**/node_modules",
    "**/__pycache__",
    ".context",
    ".web",
    ".states",
    "tmp",
    "ci-out",
    "ci/.venv",
    "**/.pytest_cache",
]
LOCK_FILES = ["pyproject.toml", "uv.lock", ".python-version"]


def base() -> dagger.Container:
    """Toolchain + locked dev deps. Source-independent, so it stays cached."""
    node = dag.container().from_(NODE_IMAGE).file("/usr/local/bin/node")
    lock = dag.host().directory(str(REPO), include=LOCK_FILES)
    return (
        dag.container()
        .from_(PYTHON_IMAGE)
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "--no-install-recommends", "git"])
        .with_exec(["pip", "install", f"uv=={UV_VERSION}"])
        .with_file("/usr/local/bin/node", node)
        .with_mounted_cache("/root/.cache/uv", dag.cache_volume("buridan-uv"))
        .with_env_variable("UV_LINK_MODE", "copy")
        .with_workdir(APP)
        .with_directory(APP, lock)
        .with_exec(["uv", "sync", "--frozen", "--no-install-project", "--group", "dev"])
    )


def with_source(ctr: dagger.Container) -> dagger.Container:
    src = dag.host().directory(str(REPO), exclude=EXCLUDE)
    return ctr.with_directory(APP, src)


async def _run(ctr: dagger.Container, name: str) -> int:
    code = await ctr.exit_code()
    print(f"[{name}] exit code {code}")
    return code


async def test(pytest_args: list[str], junit_name: str) -> int:
    out = Path(os.environ.get("CI_OUT_DIR", REPO / "ci-out"))
    await asyncio.to_thread(out.mkdir, parents=True, exist_ok=True)
    cmd = [
        "uv",
        "run",
        "--with",
        "pytest-reportlog==1.0.0",
        "pytest",
        "-q",
        "--report-log=tmp/log.json",
        f"--junitxml=tmp/junit/{junit_name}",
        "-o",
        "junit_family=xunit1",
        *pytest_args,
    ]
    ctr = (
        with_source(base())
        .with_exec(["mkdir", "-p", "tmp/junit"])
        .with_exec(cmd, expect=dagger.ReturnType.ANY)
    )
    code = await _run(ctr, "test")
    # Export results even on failure so Captain / Trunk can read them.
    await ctr.directory(f"{APP}/tmp").export(str(out))
    return code


async def validate() -> int:
    ctr = with_source(base())
    script = (
        "set -euo pipefail\n"
        "git init -q && git add -A && "
        "git -c user.email=ci@local -c user.name=ci commit -qm base\n"
        "uv run python scripts/generate_anatomy.py --check\n"
        "uv run python scripts/generate_markdown.py\n"
        "git diff --exit-code assets/docs\n"
        "uv run pytest tests/test_generated_assets.py tests/test_toc_scrollspy.py\n"
    )
    ctr = ctr.with_exec(["bash", "-c", script], expect=dagger.ReturnType.ANY)
    return await _run(ctr, "validate")


async def checker(name: str, pkg: str, version: str, args: list[str]) -> int:
    ctr = with_source(base()).with_exec(["uv", "tool", "install", f"{pkg}=={version}"])
    ctr = ctr.with_env_variable(
        "PATH",
        "/root/.local/bin:" + await ctr.env_variable("PATH"),
    )
    return await _run(ctr.with_exec(args, expect=dagger.ReturnType.ANY), name)


async def main() -> int:
    p = argparse.ArgumentParser(prog="ci")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("test")
    t.add_argument("--junit-name", default="original.xml")
    t.add_argument("pytest_args", nargs=argparse.REMAINDER)
    sub.add_parser("validate")
    for n in ("pyright", "pyrefly"):
        s = sub.add_parser(n)
        s.add_argument("paths", nargs="*")
    sub.add_parser("all")
    a = p.parse_args()

    async with dagger.connection(dagger.Config(log_output=sys.stderr)):
        if a.cmd == "test":
            return await test([x for x in a.pytest_args if x != "--"], a.junit_name)
        if a.cmd == "validate":
            return await validate()
        if a.cmd == "pyright":
            return await checker(
                "pyright",
                "pyright",
                PYRIGHT_VERSION,
                [
                    "pyright",
                    "--pythonpath",
                    ".venv/bin/python",
                    "--project",
                    "pyrightconfig.json",
                    *a.paths,
                ],
            )
        if a.cmd == "pyrefly":
            return await checker(
                "pyrefly",
                "pyrefly",
                PYREFLY_VERSION,
                ["pyrefly", "check", *a.paths],
            )
        results = [await test([], "original.xml"), await validate()]
        return int(any(results))


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
