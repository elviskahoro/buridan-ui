"""Regression tests for imports used by shared core components."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from reflex.compiler.utils import compile_imports  # noqa: E402

from components.ui.core import CN, PACKAGE_CN  # noqa: E402


def test_cn_import_renders_from_package_root() -> None:
    """The generated cn import must not include a trailing slash."""
    import_vars = dict(CN._get_all_var_data().imports)[PACKAGE_CN]
    assert len(import_vars) == 1
    assert import_vars[0].package_path == ""

    rendered_import = compile_imports({PACKAGE_CN: list(import_vars)})[0]
    assert rendered_import["lib"] == "clsx-for-tailwind"
    assert rendered_import["rest"] == ["cn"]
