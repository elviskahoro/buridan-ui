# pyright: reportUnknownMemberType=false
import ast
import importlib
import inspect
import pathlib
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import reflex as rx

from app.registry.components import COMPONENT_REGISTRY
from app.www.style import (
    HeadingIdRegistry,
    iter_heading_segments,
    markdown_component_map,
    render_heading,
    render_parse_error,
)
from app.www.wrapper import (
    chart_util_wrapper,
    cli_and_manual_installation_wrapper,
    demo_wrapper,
    tooltip_wrapper,
    usage_wrapper,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def get_all_dependencies(name: str, registry: dict[str, Any]) -> list[str]:
    """Recursively get all dependencies for a component in correct order."""
    deps: list[str] = []

    def resolve(comp_name: str) -> None:
        comp = registry.get(comp_name.lower())
        if not comp:
            return
        for dep in comp.get("dependencies", []):
            if dep not in deps:
                resolve(dep)
        if comp_name not in deps:
            deps.append(comp_name)

    resolve(name)
    return deps


def _render_demo(obj: object) -> rx.Component:
    component = cast("Callable[[], rx.Component]", obj)
    src = inspect.getsource(component).strip()
    return demo_wrapper(component(), src)


def _render_code(cmd: str, obj: object, inspect_obj: object) -> rx.Component:
    target = inspect.getmodule(inspect_obj) if "_file" in cmd else obj
    if target is None:
        msg = "could not resolve a module for the component"
        raise TypeError(msg)
    src = inspect.getsource(cast("Callable[..., object]", target)).strip()

    return chart_util_wrapper(source=src)


def _render_install(name: object) -> rx.Component:
    comp_name = str(name).lower()
    all_deps = get_all_dependencies(comp_name, COMPONENT_REGISTRY)
    if not all_deps:
        return render_parse_error(
            f"Component '{name}' not found in registry",
        )

    files_data: list[tuple[str, str]] = []
    for dep in all_deps:
        comp_info = COMPONENT_REGISTRY[dep]
        for f_path in comp_info.get("files", []):
            try:
                content = Path(f_path).read_text().strip()
                files_data.append((f_path, content))
            except (OSError, UnicodeError) as e:
                return render_parse_error(f"Error reading {f_path}: {e}")

    # `buridan add` takes component names as bare positional args;
    # qualifying the name with a `component` sub-keyword would be
    # looked up as a component name itself and trigger a spurious
    # registry warning, so render only the bare component name.
    cli_cmd = f"uv run buridan add {comp_name}"
    return cli_and_manual_installation_wrapper(cli_cmd, files_data)


def _render_usage(import_name: str, file_path: str) -> rx.Component:
    module_stem = pathlib.Path(file_path).stem if file_path else "component"
    return usage_wrapper(
        f"from components.ui.{module_stem} import {import_name}",
    )


def _render_anatomy(name: object) -> rx.Component:
    from app.registry.anatomy import ANATOMY

    src = ANATOMY.get(str(name).lower())
    if not src:
        return render_parse_error(f"No anatomy found for '{name}'")
    return rx.el.div(
        rx.el.code(
            src,
            style={
                "white-space": "pre",
                "color": "var(--foreground)",
                "font-size": "13px",
                "padding": "1rem 0.75rem",
                "display": "block",
            },
        ),
        class_name="overflow-x-auto overflow-y-auto scrollbar-none w-full mt-4 mb-8 rounded-[1rem] outline outline-input flex-1 min-h-0 flex flex-col bg-secondary dark:bg-card",
    )


class DocParser:
    """Minimal markdown parser for Reflex documentation."""

    def __init__(  # noqa: D107 - args are documented on the class
        self,
        registry: dict[str, Any] | None = None,
        dynamic_load_dirs: list[str] | None = None,
    ) -> None:
        self.registry: dict[str, Any] = registry or {}
        root = pathlib.Path(__file__).resolve().parents[2]
        for d in dynamic_load_dirs or []:
            load_dir = pathlib.Path(d)
            if not load_dir.is_absolute():
                load_dir = root / load_dir
            load_dir = load_dir.resolve()
            try:
                load_dir.relative_to(root)
            except ValueError as exc:
                msg = (
                    f"Dynamic load directory {d!r} resolves outside project root {root}"
                )
                raise ValueError(msg) from exc

            for py in load_dir.rglob("*.py"):
                if py.name.startswith("__"):
                    continue
                mod = importlib.import_module(
                    ".".join(py.relative_to(root).with_suffix("").parts),
                )
                for n, o in inspect.getmembers(mod):
                    if (
                        inspect.isfunction(o)
                        or inspect.isclass(o)
                        or inspect.ismethod(o)
                        or isinstance(o, rx.ComponentNamespace)
                    ) and getattr(o, "__module__", None) == mod.__name__:
                        self.registry[n.lower()] = (o, n)

    def _render(self, cmd: str, arg: str) -> rx.Component:

        try:
            val = (
                ast.literal_eval(arg)
                if arg and any(arg.startswith(c) for c in "[{'\"")
                else arg
            )
            name = val[0] if isinstance(val, list) else val

            registry_entry = self.registry.get(str(name).lower())
            if not registry_entry and cmd != "install":
                return render_parse_error(f"'{name}' not found")

            obj, preferred_name = (
                registry_entry if registry_entry else (None, str(name))
            )

            # Use the class for inspection if obj is an instance (like ComponentNamespace)
            inspect_obj = obj
            if obj and not (
                inspect.isclass(obj)
                or inspect.isfunction(obj)
                or inspect.ismodule(obj)
                or inspect.ismethod(obj)
            ):
                inspect_obj = getattr(obj, "__class__", obj)

            # Check if it's a chart-related component
            try:
                file_path = inspect.getfile(inspect_obj) if inspect_obj else ""
            except (TypeError, ValueError):
                file_path = ""

            # Ordered: tooltip/demo/code are substring matches, the rest exact.
            handlers: list[tuple[bool, Callable[[], rx.Component]]] = [
                ("tooltip" in cmd, tooltip_wrapper),
                ("demo" in cmd, lambda: _render_demo(obj)),
                ("code" in cmd, lambda: _render_code(cmd, obj, inspect_obj)),
                (cmd == "install", lambda: _render_install(name)),
                (cmd == "usage", lambda: _render_usage(preferred_name, file_path)),
                (cmd == "anatomy", lambda: _render_anatomy(name)),
            ]
            for matched, handler in handlers:
                if matched:
                    return handler()

            return render_parse_error(f"Unknown command: {cmd}")
        except Exception as e:  # noqa: BLE001 - render an error component, never crash the page
            return render_parse_error(f"Error in {cmd}: {e}")

    def parse_and_render(
        self,
        content: str,
        heading_registry: HeadingIdRegistry | None = None,
    ) -> list[rx.Component]:
        res: list[rx.Component] = []
        for s in re.split(r"(--[\w_]+(?:\([^)]+\))?--)", content):
            if m := re.match(r"--([\w_]+)(?:\(([^)]+)\))?--", s):
                res.append(self._render(m.group(1).lower(), m.group(2)))
                continue
            if not s.strip():
                continue

            # Split the prose chunk at every h1/h2 heading so the heading DOM
            # ids can be assigned server-side (with a HeadingIdRegistry that
            # deduplicates slugs across the whole page) instead of computed in
            # the browser from an unevaluated Reflex Var. Only the prose between
            # headings is handed to ``rx.markdown``; h3+ headings stay inside
            # those prose segments and keep their default (id-less) rendering.
            for kind, payload in iter_heading_segments(s):
                if kind == "heading":
                    level, text = payload
                    heading_id = (
                        heading_registry.next_id(text)
                        if heading_registry is not None
                        else None
                    )
                    res.append(render_heading(level, text, heading_id))
                else:
                    body = payload
                    if body.strip():
                        res.append(
                            rx.markdown(body, component_map=markdown_component_map),
                        )

        return res
