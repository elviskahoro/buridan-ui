"""Regression tests for the ``cn`` Tailwind class merge helper."""

import json
from pathlib import Path

import reflex as rx

from components.ui import core

ROOT_DIR = Path(__file__).parent.parent


def test_cn_composes_clsx_and_tailwind_merge_for_all_inputs() -> None:
    dynamic_class = rx.Var("dynamicClass")

    result = str(core.cn("p-2", ["p-4", None], ("text-sm",), dynamic_class))

    assert result == (
        '(twMerge((clsx("p-2", ["p-4", null], '
        '["text-sm"], dynamicClass))))'
    )


def test_cn_registers_named_imports_from_mit_packages() -> None:
    imports = dict(core.cn("p-2", "p-4")._get_all_var_data().imports)

    assert imports["clsx@2.1.1"][0].tag == "clsx"
    assert imports["tailwind-merge@3.7.0"][0].tag == "twMerge"


def test_frontend_dependencies_use_replacement_packages() -> None:
    package_json = json.loads(
        (ROOT_DIR / "reflex.lock" / "package.json").read_text(encoding="utf-8")
    )
    dependencies = package_json["dependencies"]

    assert dependencies["clsx"] == "2.1.1"
    assert dependencies["tailwind-merge"] == "3.7.0"
    assert "clsx-for-tailwind" not in dependencies


def test_cn_imports_declare_explicit_package_roots() -> None:
    """Keep root-level imports explicit for both class-merging packages."""
    imports = dict(core.cn("p-2", "p-4")._get_all_var_data().imports)

    assert imports["clsx@2.1.1"][0].package_path == ""
    assert imports["tailwind-merge@3.7.0"][0].package_path == ""
