import reflex as rx

from ..style import info, tooltip


def linechart_v3():
    data = [
        {"month": "Jan", "desktop": 186},
        {"month": "Feb", "desktop": 305},
        {"month": "Mar", "desktop": 237},
        {"month": "Apr", "desktop": 73},
        {"month": "May", "desktop": 209},
        {"month": "Jun", "desktop": 214},
    ]

    return rx.center(
        rx.vstack(
            info(
                "Line Chart - Label",
                "3",
                "Showing total visitors for the last 6 months",
                "start",
            ),
            rx.recharts.line_chart(
                rx.recharts.graphing_tooltip(**tooltip),
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.line(
                    rx.recharts.label_list(
                        position="top",
                        offset=20,
                        custom_attrs={"fontSize": "12px", "fontWeight": "bold"},
                    ),
                    data_key="desktop",
                    stroke=rx.color("accent", 8),
                    stroke_width=2,
                    type_="linear",
                    dot=True,
                ),
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
                margin={"left": 20, "right": 20, "top": 25},
            ),
            info("Trending up by 5.2% this month", "2", "January - June 2024", "start"),
            class_name="w-[100%] [&_.recharts-tooltip-item-separator]:w-full",
        ),
        width="100%",
        padding="0.5em",
    )
