"""Regression tests for the recharts Tooltip wiring in chart blocks.

`bar_chart_04` originally shipped ``chart_tooltip_content(...)`` card-root
styling without rendering the matching ``chart_tooltip()`` component inside its
``rx.recharts.bar_chart``, so hovering the temperature chart showed nothing.
These tests pin the pairing rule ("tooltip styling ⇔ tooltip component") so
the same slip cannot recur on ``bar_chart_04`` or any future chart block.
"""

# ruff: noqa: INP001, E402

import importlib
import inspect
import pkgutil
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.blocks import bar_chart_04

_BAR_CHART_TAG = "BarChart"
_TOOLTIP_TAG = "Tooltip"
_CHART_TAGS = {_BAR_CHART_TAG, "LineChart", "AreaChart"}


def _walk(node: object) -> Iterator[object]:
    yield node
    for child in getattr(node, "children", ()) or ():
        yield from _walk(child)


def test_bar_chart_04_renders_graphing_tooltip_as_first_child() -> None:
    """The temperature ``BarChart`` must lead with the ``chart_tooltip()`` child."""
    block = bar_chart_04.bar_chart_04()
    charts = [
        node for node in _walk(block) if getattr(node, "tag", None) == _BAR_CHART_TAG
    ]
    assert charts, "No BarChart in component tree"
    for chart in charts:
        children = list(getattr(chart, "children", ()) or ())
        assert children, "BarChart has no children"
        first = children[0]
        assert type(first).__name__ == "GraphingTooltip"
        assert first.tag == _TOOLTIP_TAG


def test_every_block_using_chart_tooltip_content_renders_chart_tooltip() -> None:
    """Any block that applies ``chart_tooltip_content`` styling must also render
    a ``chart_tooltip()`` child — otherwise the styling is dead code and the
    chart has no hover tooltip, which is the ``bar_chart_04`` regression.
    """
    import app.www.library.blocks as blocks_pkg

    offenders: list[str] = []
    for mod_info in pkgutil.iter_modules(blocks_pkg.__path__):
        mod = importlib.import_module(f"app.www.library.blocks.{mod_info.name}")
        factory = getattr(mod, mod_info.name, None)
        if factory is None or not callable(factory):
            continue
        if "chart_tooltip_content" not in inspect.getsource(mod):
            continue
        rendered = factory()
        rendered_class = getattr(rendered, "class_name", None)
        if rendered_class is None or "recharts-tooltip" not in str(rendered_class):
            continue
        has_tooltip = any(
            getattr(child, "tag", None) == _TOOLTIP_TAG
            for node in _walk(rendered)
            if getattr(node, "tag", None) in _CHART_TAGS
            for child in getattr(node, "children", ()) or ()
        )
        if not has_tooltip:
            offenders.append(mod_info.name)
    msg = f"blocks shipping tooltip styling but no tooltip: {offenders}"
    assert not offenders, msg
