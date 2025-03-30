from __future__ import annotations

from functools import wraps
from typing import Callable

import reflex as rx
from .view_code import view_code
from ...ui.atoms.buttons import button_with_icon, button_with_link


def extract_chart_info(path):
    import re

    # Regex pattern to match both 'charts' and 'pantry' base paths
    match = re.search(r"(charts|pantry)/([a-zA-Z]+)/v(\d+)", path)
    if match:
        # category = match.group(1)  # 'charts' or 'pantry'
        chart_name = match.group(2)  # 'area', 'animations', etc.
        version = match.group(3)  # Version number

        # Use rx.hstack to display as 'animations > v1', etc.
        return rx.hstack(
            rx.el.label(
                chart_name,
                class_name="text-sm font-regular",
                color=rx.color("slate", 11),
            ),
            rx.el.label(
                "›", class_name="text-sm font-medium", color=rx.color("slate", 11)
            ),
            rx.el.label(
                f"v{version}",
                class_name="text-sm font-medium",
                color=rx.color("slate", 12),
            ),
            spacing="1",
        )
    raise ValueError(
        f"Error: Path '{path}' is invalid or not in the expected format (charts/pantry/...). Please check your input."
    )


def component_wrapper(path: str):
    def decorator(func: Callable[[], list[rx.Component | str | int]]):
        @wraps(func)
        def wrapper():
            component, component_code, flexgen_path = func()

            return rx.box(
                rx.box(
                    rx.el.label(
                        extract_chart_info(path),
                        class_name="text-sm",
                    ),
                    rx.box(
                        view_code(component, component_code),
                        button_with_icon(
                            "clipboard",
                            on_click=[
                                rx.set_clipboard(component_code),
                                rx.toast(
                                    "Copied to clipboard!",
                                    position="top-center",
                                ),
                            ],
                        ),
                        button_with_link("github", path),
                        class_name="flex align-center gap-2",
                    ),
                    # border_bottom=f"0.81px solid {rx.color('gray', 5)}",
                    class_name="px-5 pt-4 pb-2 w-full flex align-center justify-between items-center",
                ),
                rx.box(
                    component,
                    class_name="rounded-xl h-full w-full flex align-center justify-center items-center py-6 px-4",
                ),
                border=f"1px dashed {rx.color('gray', 5)}",
                class_name="rounded-xl shadow-sm size-full flex flex-col",
            )

        return wrapper

    return decorator
