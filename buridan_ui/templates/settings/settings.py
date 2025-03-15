import reflex as rx
from reflex.experimental import ClientStateVar

color = [
    "gray",
    "ruby",
    "pink",
    "purple",
    "blue",
    "cyan",
    "teal",
    "grass",
    "orange",
    "yellow",
    "amber",
    "bronze",
]


SiteThemeColor = ClientStateVar.create("site_theme_color", "blue")


def app_settings():
    return rx.popover.root(
        rx.popover.trigger(
            rx.box(
                rx.icon(
                    tag="settings",
                    size=13,
                    color=rx.color("slate", 11),
                    _hover={"color": rx.color("slate", 12)},
                ),
                _hover={"background": rx.color("gray", 3)},
                class_name="cursor-pointer rounded-lg py-1 px-2 flex items-center justify-center",
            )
        ),
        rx.popover.content(
            rx.el.div(
                rx.el.div(
                    rx.el.label("Buridan Stack", class_name="text-sm font-bold"),
                    rx.el.label(
                        "Navigate between buridan stacks.",
                        class_name="text-xs font-light "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    rx.el.div(
                        rx.link(
                            rx.box(
                                rx.el.label(
                                    "ui",
                                    color=rx.color("slate", 11),
                                    class_name="text-md font-bold",
                                ),
                                border_top=f"1.25px dashed {rx.color('blue', 5)}",
                                border_bottom=f"1.25px dashed {rx.color('blue', 5)}",
                                color=rx.color("blue", 8),
                                class_name="h-full p-4 col-start-2 row-span-full row-start-1 max-sm:hidden bg-[size:10px_10px] bg-fixed bg-[image:repeating-linear-gradient(315deg,currentColor_0,currentColor_1px,_transparent_0,_transparent_50%)] flex justify-center align-center items-center hover:brightness-125",
                            ),
                            href="/",
                            is_external=True,
                            text_decoration="none",
                            class_name="size-full cursor:pointer",
                        ),
                        rx.link(
                            rx.box(
                                rx.el.label(
                                    "ui",
                                    color=rx.color("slate", 11),
                                    class_name="text-md font-bold",
                                ),
                                border_top=f"1.25px dashed {rx.color('grass', 5)}",
                                border_bottom=f"1.25px dashed {rx.color('grass', 5)}",
                                color=rx.color("grass", 8),
                                class_name="h-full p-4 col-start-2 row-span-full row-start-1 max-sm:hidden bg-[size:10px_10px] bg-fixed bg-[image:repeating-linear-gradient(315deg,currentColor_0,currentColor_1px,_transparent_0,_transparent_50%)] flex justify-center align-center items-center hover:brightness-125",
                            ),
                            is_external=True,
                            href="https://buridan-lab.reflex.run/",
                            text_decoration="none",
                            class_name="w-full cursor:pointer",
                        ),
                        class_name="flex flex-row w-full",
                    ),
                    class_name="flex flex-col w-full gap-y-2 p-4",
                ),
                rx.divider(
                    border_bottom=f"1.25px dashed {rx.color('gray', 5)}",
                    bg="transparent",
                ),
                rx.el.div(
                    rx.el.label("Site Theme", class_name="text-sm font-bold"),
                    rx.el.label(
                        "Use to visualize charts in different colors.",
                        class_name="text-xs font-light "
                        + rx.color_mode_cond("text-slate-700", "text-slate-200"),
                    ),
                    rx.el.div(
                        *[
                            rx.el.div(
                                bg=rx.color(index),
                                on_click=SiteThemeColor.set_value(index),
                                class_name="size-4 p-2 rounded-full cursor-pointer hover:brightness-125",
                            )
                            for index in color
                        ],
                        class_name="flex flex-row gap-2 w-full flex-wrap",
                    ),
                    class_name="flex flex-col w-full gap-y-2 p-4",
                ),
                class_name="w-[320px] flex flex-col gap-y-0 p-0",
            ),
            size="1",
            border=f"1.25px dashed {rx.color('gray', 5)}",
            class_name="shadow-md p-0",
        ),
    )
