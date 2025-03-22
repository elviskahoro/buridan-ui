from __future__ import annotations

import reflex as rx
from reflex.constants.colors import Color
from reflex.experimental import ClientStateVar


from buridan_ui.static.routes import ChartRoutes, PantryRoutes, GettingStartedRoutes
from buridan_ui.static.scripts import count_python_files_in_folder
from buridan_ui.templates.sidemenu.download import download_site_source

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
                    rx.color_mode.icon(
                        light_component=rx.icon(
                            "moon",
                            size=11,
                            color=rx.color("slate", 11),
                        ),
                        dark_component=rx.icon(
                            "sun",
                            size=11,
                            color=rx.color("slate", 11),
                        ),
                    ),
                    title="Toggle theme",
                    on_click=rx.toggle_color_mode,
                    _hover={"background": rx.color("gray", 3)},
                    border=f"0.81px solid {rx.color('gray', 5)}",
                    class_name="flex flex-row cursor-pointer rounded-md flex items-center justify-center align-center p-1",
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


def sidemenu(in_drawer=False):
    return rx.scroll_area(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.link(
                        rx.el.label(
                            f"buridan/ui",
                            class_name="text-sm font-bold font-sans flex items-center align-center gap-x-2 cursor-pointer "
                            + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                        ),
                        text_decoration="none",
                        href="/",
                    ),
                    rx.el.label(
                        "v.0.6.1",
                        class_name="text-xs font-medium",
                        color=rx.color("slate", 11),
                    ),
                    class_name="w-full flex flex-row justify-between align-end items-end",
                ),
                border_bottom=f"1.25px dashed {rx.color('gray', 5)}",
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
                    download_site_source(),
                    _menu_settings("Source", "github"),
                    spacing="2",
                ),
                _site_settings,
            ),
            rx.divider(
                border_bottom=f"1.25px dashed {rx.color('gray', 5)}", bg="transparent"
            ),
            side_bar_wrapper(
                "Getting Started",
                rx.el.div(
                    rx.el.label(
                        "Quickly set up and get started with the basics of buridan/ui.",
                        class_name="text-sm font-light pt-1 pb-2 "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    rx.el.div(
                        rx.box(
                            border_left=f"1.25px dashed {rx.color('accent', 7)}",
                            border_right=f"1.25px dashed {rx.color('accent', 7)}",
                            color=rx.color("accent", 6),
                            class_name="w-[4px] col-start-2 row-span-full row-start-1 bg-[size:10px_10px] bg-fixed bg-[image:repeating-linear-gradient(315deg,currentColor_0,currentColor_1px,_transparent_0,_transparent_50%)]",
                        ),
                        create_sidebar_menu_items(GettingStartedRoutes),
                        class_name="flex flex-row h-full w-full gap-x-2",
                    ),
                    class_name="flex flex-col p-0 m-0",
                ),
                _getting_started,
            ),
            rx.divider(
                border_bottom=f"1.25px dashed {rx.color('gray', 5)}", bg="transparent"
            ),
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
                    rx.el.div(
                        rx.box(
                            border_left=f"1.25px dashed {rx.color('accent', 7)}",
                            border_right=f"1.25px dashed {rx.color('accent', 7)}",
                            color=rx.color("accent", 6),
                            class_name="w-[4px] col-start-2 row-span-full row-start-1 bg-[size:10px_10px] bg-fixed bg-[image:repeating-linear-gradient(315deg,currentColor_0,currentColor_1px,_transparent_0,_transparent_50%)]",
                        ),
                        create_sidebar_menu_items(ChartRoutes),
                        class_name="flex flex-row h-full w-full gap-x-2",
                    ),
                    class_name="flex flex-col p-0 m-0",
                ),
                _chart_components,
            ),
            rx.divider(
                border_bottom=f"1.25px dashed {rx.color('gray', 5)}", bg="transparent"
            ),
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
                    rx.el.div(
                        rx.box(
                            border_left=f"1.25px dashed {rx.color('accent', 7)}",
                            border_right=f"1.25px dashed {rx.color('accent', 7)}",
                            color=rx.color("accent", 6),
                            class_name="w-[4px] col-start-2 row-span-full row-start-1 bg-[size:10px_10px] bg-fixed bg-[image:repeating-linear-gradient(315deg,currentColor_0,currentColor_1px,_transparent_0,_transparent_50%)]",
                        ),
                        create_sidebar_menu_items(PantryRoutes),
                        class_name="flex flex-row h-full w-full gap-x-2",
                    ),
                    class_name="flex flex-col p-0 m-0",
                ),
                _pantry_components,
            ),
            class_name="flex flex-col w-full h-full pt-12",
        ),
        height="100vh",
        class_name="flex flex-col max-w-[300px] w-full gap-y-2 align-start sticky top-0 left-0 [&_.rt-ScrollAreaScrollbar]:mr-[0.1875rem] z-[10]",
        display=(
            ["none" if i <= 3 else "flex" for i in range(6)]
            if not in_drawer
            else "flex"
        ),
    )
