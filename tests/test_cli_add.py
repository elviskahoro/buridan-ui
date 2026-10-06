"""Regression test for ``buridan add`` (``cli.main.cmd_add``).

Runs the REAL ``add_components_to_project`` copy loop (no monkeypatching)
against a throwaway Reflex project skeleton under ``tmp_path``, mirroring the
bug report's reproduction. Source components resolve to this checkout's
``components/`` tree via ``get_source_root()``.

Guards against the footgun where ``cmd_add``'s body was duplicated: every
successful run copied each dependency file twice and printed every status
line (and the no-theme warning) twice. Pinning each ``Added`` line and the
warning to exactly one occurrence fails fast if the duplication is reintroduced.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from cli.main import cmd_add, get_source_root

# The ``button`` component pulls in ``core`` via resolve_dependencies; both
# files must be copied exactly once.
EXPECTED_FILES = ["components/ui/button.py", "components/ui/core.py"]


def test_cmd_add_copies_each_dependency_file_exactly_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    # No theme in assets/globals.css -> the no-theme warning fires. This is the
    # bug report's reproduction against a real project skeleton under tmp_path.
    (tmp_path / "rxconfig.py").write_text("# stub rxconfig\n", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "globals.css").write_text(
        "/* no theme here */\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    cmd_add(["button"])

    out = capsys.readouterr().out
    source_root = get_source_root()
    assert source_root is not None, "tests must run in-tree with a components/ dir"

    # Each dependency file is announced and copied exactly once.
    for rel in EXPECTED_FILES:
        assert out.count(f"Added {rel}") == 1, out
        dest = tmp_path / rel
        assert dest.exists(), dest
        assert dest.read_bytes() == (source_root / rel).read_bytes()

    # The no-theme warning appears exactly once (the bug printed it twice).
    assert out.count("No theme detected in assets/globals.css.") == 1, out
