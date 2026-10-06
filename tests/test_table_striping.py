"""Regression tests for the ``table`` component's ``striped`` handling.

``striped`` is a declared keyword parameter of only the high-level ``table(...)``
builder (``HighLevelTable.create``). The low-level ``table.root(...)`` builder
(``TableRoot.create``) does not declare it, so passing ``striped=True`` there
leaks the kwarg onto the component ``style`` dict (rendered as an inert Emotion
``css`` rule that browsers discard) and no zebra striping is applied.

These tests guard the two invariants that matter going forward:

* the high-level ``table(...)`` builder honors ``striped`` (and consumes it, never
  leaking it), and
* ``table.root(...)`` does **not** handle ``striped`` — a tripwire so that a
  future change adding ``striped`` support to ``TableRoot`` is deliberate and
  reviewed, not a silent side effect.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.table import TableRoot, table


def test_high_level_table_striped_true_adds_striping() -> None:
    rendered = str(table(data=[{"a": str(i)} for i in range(4)], striped=True).render())
    assert "even:bg-secondary/30" in rendered
    assert "striped" not in rendered


def test_high_level_table_default_has_no_striping() -> None:
    assert "even:bg-secondary/30" not in str(
        table(data=[{"a": str(i)} for i in range(4)]).render()
    )


def test_passing_striped_to_table_root_leaks_into_style() -> None:
    """``TableRoot.create`` does not declare ``striped``; passing it leaks the
    kwarg onto the component ``style`` dict (rendered as an inert CSS rule).

    This leak is the root cause the example cards shipped without striping. The
    cards now apply ``even:bg-secondary/30`` to body rows directly. Locking the
    leak here ensures a future change that starts consuming ``striped`` on
    ``TableRoot`` is a deliberate, reviewed decision — not a silent one — at
    which point the cards can revert to the ``striped=True`` form.
    """
    root = TableRoot.create(
        table.header(table.row(table.head("h"))),
        table.body(table.row(table.cell("x"))),
        striped=True,
        class_name="border-none",
    )
    assert "striped" in dict(getattr(root, "style", {}) or {})
    assert "striped" in str(root.render())
