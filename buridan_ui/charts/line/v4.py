import reflex as rx

from ..style import info, tooltip


def linechart_v4():
    data = [
        {"month": "Jan", "desktop": 186, "mobile": 80},
        {"month": "Feb", "desktop": 305, "mobile": 200},
        {"month": "Mar", "desktop": 237, "mobile": 120},
        {"month": "Apr", "desktop": 73, "mobile": 190},
        {"month": "May", "desktop": 209, "mobile": 130},
        {"month": "Jun", "desktop": 214, "mobile": 140},
    ]

    return rx.center(
        rx.vstack(
            info(
                "Line Chart - Multiple",
                "3",
                "Showing total visitors for the last 6 months",
                "start",
            ),
            rx.recharts.line_chart(
                rx.recharts.graphing_tooltip(**tooltip),
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                *[
                    rx.recharts.line(
                        data_key=name,
                        stroke=rx.color("accent", 7 + index),
                        stroke_width=2,
                        type_="natural",
                        dot=False,
                        stack_id="a",
                    )
                    for index, name in enumerate(["desktop", "mobile"])
                ],
                rx.recharts.x_axis(
                    data_key="month",
                    axis_line=False,
                    tick_size=10,
                    tick_line=False,
                    custom_attrs={"fontSize": "12px"},
                    interval="preserveStartEnd",
                ),
                data=data,
                width="100%",
                height=250,
            ),
            info("Trending up by 5.2% this month", "2", "January - June 2024", "start"),
            class_name="w-[100%] [&_.recharts-tooltip-item-separator]:w-full",
        ),
        width="100%",
        padding="0.5em",
    )
