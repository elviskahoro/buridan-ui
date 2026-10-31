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
from collections.abc import Callable, Iterator
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.blocks import bar_chart_04

_BAR_CHART_TAG = "BarChart"
_TOOLTIP_TAG = "Tooltip"
_CHART_TAGS = {_BAR_CHART_TAG, "LineChart", "AreaChart"}

_CHARTS_ROOT = ROOT_DIR / "app" / "www" / "library" / "charts"


def _walk(node: object) -> Iterator[object]:
    yield node
    for child in getattr(node, "children", ()) or ():
        yield from _walk(child)


def _has_tooltip_child(rendered: object) -> bool:
    """True if any chart in ``rendered`` ships a ``Tooltip`` child."""
    return any(
        getattr(child, "tag", None) == _TOOLTIP_TAG
        for node in _walk(rendered)
        if getattr(node, "tag", None) in _CHART_TAGS
        for child in getattr(node, "children", ()) or ()
    )


def _factory_in(mod: object, modname: str) -> Callable[[], object] | None:
    """Top-level public function defined in ``mod`` itself (the block factory)."""
    factories = [
        member
        for _name, member in inspect.getmembers(mod, inspect.isfunction)
        if member.__module__ == modname and not member.__name__.startswith("_")
    ]
    return factories[0] if len(factories) == 1 else None


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
        modname = f"app.www.library.blocks.{mod_info.name}"
        mod = importlib.import_module(modname)
        factory = getattr(mod, mod_info.name, None)
        if factory is None or not callable(factory):
            continue
        if "chart_tooltip_content" not in inspect.getsource(mod):
            continue
        rendered = factory()
        rendered_class = getattr(rendered, "class_name", None)
        if rendered_class is None or "recharts-tooltip" not in str(rendered_class):
            continue
        if not _has_tooltip_child(rendered):
            offenders.append(mod_info.name)
    msg = f"blocks shipping tooltip styling but no tooltip: {offenders}"
    assert not offenders, msg


def test_every_chart_using_chart_tooltip_content_renders_chart_tooltip() -> None:
    """The pairing rule also covers ``app.www.library.charts`` — the live
    ``/charts`` pages render these factories, so a slip there is user-visible
    the same way ``bar_chart_04``'s was. ``charts/`` modules live in nested
    packages (``bar/v1.py`` defines ``barchart_v1``; ``bar/docex_4.py`` defines
    ``chart_example_with_custom_tooltip``), so the factory name rarely matches
    the module name and must be discovered via ``inspect.getmembers``.
    """
    offenders: list[str] = []
    for module_path in sorted(_CHARTS_ROOT.rglob("*.py")):
        if module_path.name in {"chart_tooltip.py", "__init__.py"}:
            continue
        rel = module_path.relative_to(_CHARTS_ROOT).with_suffix("")
        modname = "app.www.library.charts." + ".".join(rel.parts)
        mod = importlib.import_module(modname)
        if "chart_tooltip_content" not in inspect.getsource(mod):
            continue
        factory = _factory_in(mod, modname)
        if factory is None:
            continue
        rendered = factory()
        rendered_class = getattr(rendered, "class_name", None)
        if rendered_class is None or "recharts-tooltip" not in str(rendered_class):
            continue
        if not _has_tooltip_child(rendered):
            offenders.append(modname)
    msg = f"charts shipping tooltip styling but no tooltip: {offenders}"
    assert not offenders, msg
