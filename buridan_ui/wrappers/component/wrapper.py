from __future__ import annotations

from functools import wraps
from typing import Callable

import reflex as rx
from .view_code import view_code
from ...ui.atoms.buttons import button_with_icon, button_with_link


def component_wrapper(path: str):
    def decorator(func: Callable[[], list[rx.Component | str | int]]):
        @wraps(func)
        def wrapper():
            component, component_code, flexgen_path = func()

            return rx.box(
                rx.box(
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
                    border_bottom=f"0.81px solid {rx.color('gray', 5)}",
                    class_name="px-4 py-3 w-full flex align-center justify-end shadow-sm",
                ),
                rx.box(
                    component,
                    class_name="rounded-xl h-full w-full flex align-center justify-center items-center py-6 px-4",
                ),
                border=f"0.81px solid {rx.color('gray', 5)}",
                class_name=f"rounded-xl shadow-sm size-full flex flex-col",
            )

        return wrapper

    return decorator
