"""Regression tests for imports used by shared core components."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from reflex.compiler.utils import compile_imports  # noqa: E402

from components.ui.core import (  # noqa: E402
    PACKAGE_CLSX,
    PACKAGE_TAILWIND_MERGE,
    cn,
)


def test_cn_imports_render_from_package_roots() -> None:
    """Imports propagated by cn() must not include trailing slashes."""
    import_map = dict(cn("p-2")._get_all_var_data().imports)
    expected_imports = {
        PACKAGE_CLSX: "clsx",
        PACKAGE_TAILWIND_MERGE: "twMerge",
    }

    assert set(import_map) == set(expected_imports)
    for package, tag in expected_imports.items():
        import_vars = import_map[package]
        assert len(import_vars) == 1
        assert import_vars[0].tag == tag
        assert import_vars[0].package_path == ""

    rendered_imports = compile_imports(
        {package: list(import_vars) for package, import_vars in import_map.items()}
    )
    assert {
        imported["lib"]: imported["rest"] for imported in rendered_imports
    } == {"clsx": ["clsx"], "tailwind-merge": ["twMerge"]}
