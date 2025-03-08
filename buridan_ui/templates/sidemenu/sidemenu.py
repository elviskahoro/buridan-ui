from __future__ import annotations

import reflex as rx
from reflex.constants.colors import Color
from reflex.experimental import ClientStateVar

from buridan_ui.states.routing import SiteRoutingState
from buridan_ui.templates.wrapper.wrapper import menu_wrapper

from .style import SideMenuStyle


def count_python_files_in_folder(folder_name):
    import os

    total_files = 0

    for _dirpath, _dirnames, filenames in os.walk(folder_name):
        total_files += len([f for f in filenames if f.endswith(".py")])

    return total_files


def color_scheme():
    from ...wrappers.base.main import dynamic_color

    return rx.el.div(
        rx.el.label(
            "Chart Colors",
            class_name="text-sm font-regular "
            + rx.color_mode_cond("text-slate-700", "text-slate-200"),
        ),
        rx.el.div(
            rx.el.label(
                rx.el.input(
                    type="radio",
                    name="text",
                    class_name="peer hidden",
                    default_checked=True,
                ),
                rx.el.div(
                    class_name="size-4 p-2 rounded-full bg-blue-500 peer-checked:outline-2 peer-checked:outline outline-1 outline-blue-700 outline-offset-4 outline-current cursor-pointer",
                ),
                on_click=rx.call_function(dynamic_color.set_value("blue")),
                class_name="cursor-pointer",
            ),
            rx.el.label(
                rx.el.input(type="radio", name="text", class_name="peer hidden"),
                rx.el.div(
                    class_name="size-4 p-2 rounded-full bg-green-500 peer-checked:outline-2 peer-checked:outline outline-1 outline-green-700 outline-offset-4 outline-current cursor-pointer",
                ),
                on_click=rx.call_function(dynamic_color.set_value("grass")),
                class_name="cursor-pointer",
            ),
            rx.el.label(
                rx.el.input(type="radio", name="text", class_name="peer hidden"),
                rx.el.div(
                    class_name="size-4 p-2 rounded-full bg-red-500 peer-checked:outline-2 peer-checked:outline outline-1 outline-red-700 outline-offset-4 outline-current cursor-pointer",
                ),
                on_click=rx.call_function(dynamic_color.set_value("red")),
                class_name="cursor-pointer",
            ),
            rx.el.label(
                rx.el.input(type="radio", name="text", class_name="peer hidden"),
                rx.el.div(
                    class_name="size-4 p-2 rounded-full bg-purple-500 peer-checked:outline-2 peer-checked:outline outline-1 outline-purple-700 outline-offset-4 outline-current cursor-pointer",
                ),
                on_click=rx.call_function(dynamic_color.set_value("purple")),
                class_name="cursor-pointer",
            ),
            class_name="flex flex-row gap-x-3 items-center",
        ),
        class_name="w-full flex flex-row justify-between align-center items-center",
    )


_site_settings = ClientStateVar.create("site_settings", False)
_getting_started = ClientStateVar.create("getting_started", False)
_chart_components = ClientStateVar.create("chart", False)
_pantry_components = ClientStateVar.create("pantry", False)


def _menu_settings(title: str, icon: str, is_theme=False):
    return rx.el.div(
        rx.el.label(
            title,
            class_name="text-sm font-regular "
            + rx.color_mode_cond("text-slate-700", "text-slate-200"),
        ),
        rx.el.div(
            (
                rx.link(
                    rx.box(
                        rx.icon(
                            tag=icon,
                            size=11,
                            color=rx.color("slate", 11),
                            _hover={"color": rx.color("slate", 12)},
                        ),
                        _hover={"background": rx.color("gray", 3)},
                        border=f"0.81px solid {rx.color('gray', 5)}",
                        class_name="flex flex-row cursor-pointer rounded-md flex items-center justify-center align-center p-1",
                    ),
                    href="https://github.com/buridan-ui/ui",
                    is_external=True,
                )
                if not is_theme
                else rx.box(
                    rx.color_mode.switch(
                        size="1",
                        class_name="cursor-pointer",
                    ),
                    title="Toggle theme",
                )
            ),
        ),
        class_name="w-full flex flex-row justify-between align-center items-center",
    )


def side_bar_wrapper(title: str, component, state: ClientStateVar):
    return rx.el.div(
        state,
        rx.el.div(
            rx.el.label(title, class_name="text-sm font-bold"),
            rx.el.div(
                rx.box(
                    rx.cond(
                        state.value,
                        rx.icon(
                            tag="plus",
                            size=11,
                            color=rx.color("slate", 11),
                            _hover={"color": rx.color("slate", 12)},
                        ),
                        rx.icon(
                            tag="minus",
                            size=11,
                            color=rx.color("slate", 11),
                            _hover={"color": rx.color("slate", 12)},
                        ),
                    ),
                    _hover={"background": rx.color("gray", 3)},
                    border=f"0.81px solid {rx.color('gray', 5)}",
                    class_name="flex flex-row cursor-pointer rounded-md flex items-center justify-center align-center p-1",
                    on_click=rx.call_function(state.set_value(~state.value)),
                ),
            ),
            class_name="w-full flex flex-row justify-between align-center items-center",
        ),
        rx.cond(
            state.value,
            rx.el.div(class_name="hidden"),
            component,
        ),
        class_name="flex flex-col w-full gap-y-2 p-4",
    )


def create_sidebar_menu_items(routes: list[dict[str, str | Color]]):

    def item(data):
        return rx.el.div(
            rx.link(
                rx.el.label(
                    data["name"],
                    _hover={"color": rx.color("slate", 12)},
                    class_name="text-sm font-regular cursor-pointer "
                    + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                ),
                href=data["path"],
                text_decoration="none",
            ),
            class_name="w-full",
        )

    return rx.vstack(
        rx.foreach(routes, item),
        spacing="0",
        width="100%",
    )


def _sidemenu() -> rx.vstack:
    return rx.vstack(
        rx.vstack(
            menu_wrapper(
                "Getting Started",
                [create_sidebar_menu_items(SiteRoutingState.GettingStartedRoutes)],
            ),
            menu_wrapper(
                "Analytics Components",
                [create_sidebar_menu_items(SiteRoutingState.AnalyticsRoutes)],
            ),
            menu_wrapper(
                "Chart Components",
                [create_sidebar_menu_items(SiteRoutingState.ChartRoutes)],
            ),
            menu_wrapper(
                "Pantry Components",
                [create_sidebar_menu_items(SiteRoutingState.PantryRoutes)],
            ),
            **SideMenuStyle.content,
        ),
        **SideMenuStyle.base,
    )


def sidemenu():
    return rx.scroll_area(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        f"buridan/ui",
                        class_name="text-sm font-bold font-sans flex items-center align-center gap-x-2",
                    ),
                ),
                border_bottom=f"0.81px solid {rx.color('gray', 3)}",
                border_right=f"0.81px solid {rx.color('gray', 3)}",
                bg=rx.color("gray", 2),
                class_name="w-full h-12 px-4 py-3 absolute top-0 left-0 z-[99]",
            ),
            side_bar_wrapper(
                "Site Settings",
                rx.vstack(
                    rx.el.label(
                        "The visual appearance of the site can be customized using the theme settings.",
                        class_name="text-sm font-light pt-1 pb-2 "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    _menu_settings("Light/Dark Mode", "", True),
                    color_scheme(),
                    _menu_settings("Source", "github"),
                    spacing="2",
                ),
                _site_settings,
            ),
            rx.divider(border=f"0.81px solid {rx.color('gray', 3)}"),
            side_bar_wrapper(
                "Getting Started",
                rx.el.div(
                    rx.el.label(
                        "Quickly set up and get started with the basics of buridan/ui.",
                        class_name="text-sm font-light pt-1 pb-2 "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    create_sidebar_menu_items(SiteRoutingState.GettingStartedRoutes),
                    class_name="flex flex-col p-0 m-0",
                ),
                _getting_started,
            ),
            rx.divider(border=f"0.81px solid {rx.color('gray', 3)}"),
            side_bar_wrapper(
                "Chart Components",
                rx.el.div(
                    rx.el.label(
                        "A collection of ",
                        rx.el.span(
                            f"{count_python_files_in_folder('buridan_ui/charts')} ",
                            class_name="text-sm font-bold",
                        ),
                        "chart components to help visualize data, build dashboards, and more.",
                        class_name="text-sm font-light pt-1 pb-2 "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    create_sidebar_menu_items(SiteRoutingState.ChartRoutes),
                    class_name="flex flex-col p-0 m-0",
                ),
                _chart_components,
            ),
            rx.divider(border=f"0.81px solid {rx.color('gray', 3)}"),
            side_bar_wrapper(
                "Pantry Components",
                rx.el.div(
                    rx.el.label(
                        "A set of ",
                        rx.el.span(
                            f"{count_python_files_in_folder('buridan_ui/pantry')} ",
                            class_name="text-sm font-bold",
                        ),
                        "components to help build and customize your interface with ease.",
                        class_name="text-sm font-light pt-1 pb-2 "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    create_sidebar_menu_items(SiteRoutingState.PantryRoutes),
                    class_name="flex flex-col p-0 m-0",
                ),
                _pantry_components,
            ),
            border_right=f"1px solid {rx.color('gray', 3)}",
            class_name="flex flex-col w-full h-full pt-11",
        ),
        height="100vh",
        class_name="flex flex-col max-w-[300px] w-full gap-y-2 align-start sticky top-0 left-0 [&_.rt-ScrollAreaScrollbar]:mr-[0.1875rem] z-[10]",
        display=["none" if i <= 3 else "flex" for i in range(6)],
    )


# rx.el.label(
#         rx.el.div(
#             rx.el.input(
#                 id="theme-1",
#                 class_name="appearance-none forced-colors:appearance-auto",
#                 type="radio",
#                 checked=True,
#                 name="themes",
#             ),
#             rx.el.p(
#                 "Cyan",
#                 class_name="hidden forced-colors:block",
#             ),
#             rx.el.div(
#                 class_name="absolute top-3 left-3 h-6 w-6 rounded-full bg-cyan-200 forced-colors:hidden",
#             ),
#             rx.el.div(
#                 class_name="absolute right-3 bottom-3 h-6 w-6 rounded-full bg-cyan-500 ring-2 ring-current forced-colors:hidden",
#             ),
#             class_name="relative grid h-16 w-16 items-center justify-center rounded-xl border border-transparent bg-transparent text-white hover:bg-gray-50 has-checked:border-cyan-500 has-checked:bg-cyan-50 has-checked:text-cyan-50 dark:text-gray-800 dark:hover:bg-gray-800 dark:has-checked:bg-cyan-950 dark:has-checked:text-cyan-950 forced-colors:border-0",
#         ),
#         class_name="text-sm font-medium text-gray-700 dark:text-white",
#     )

# <label for="theme-1" class="text-sm font-medium text-gray-700 dark:text-white">
#   <div class="relative grid h-16 w-16 items-center justify-center rounded-xl border border-transparent bg-transparent text-white hover:bg-gray-50 has-checked:border-cyan-500 has-checked:bg-cyan-50 has-checked:text-cyan-50 dark:text-gray-800 dark:hover:bg-gray-800 dark:has-checked:bg-cyan-950 dark:has-checked:text-cyan-950 forced-colors:border-0"><input id="theme-1" class="appearance-none forced-colors:appearance-auto" type="radio" checked="" name="themes"><p class="hidden forced-colors:block">Cyan</p><div class="absolute top-3 left-3 h-6 w-6 rounded-full bg-cyan-200 forced-colors:hidden"></div><div class="absolute right-3 bottom-3 h-6 w-6 rounded-full bg-cyan-500 ring-2 ring-current forced-colors:hidden"></div></div></label>
