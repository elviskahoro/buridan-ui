import reflex as rx

from buridan_ui.private._area_bump import area_bump_chart


def bump_v1():
    data = [
        {
            "id": "JavaScript",
            "data": [
                {"x": 2000, "y": 25},
                {"x": 2001, "y": 27},
                {"x": 2002, "y": 30},
                {"x": 2003, "y": 28},
                {"x": 2004, "y": 32},
                {"x": 2005, "y": 35},
            ],
        },
        {
            "id": "Python",
            "data": [
                {"x": 2000, "y": 13},
                {"x": 2001, "y": 15},
                {"x": 2002, "y": 18},
                {"x": 2003, "y": 22},
                {"x": 2004, "y": 26},
                {"x": 2005, "y": 30},
            ],
        },
        {
            "id": "Java",
            "data": [
                {"x": 2000, "y": 30},
                {"x": 2001, "y": 31},
                {"x": 2002, "y": 28},
                {"x": 2003, "y": 25},
                {"x": 2004, "y": 24},
                {"x": 2005, "y": 22},
            ],
        },
        {
            "id": "C++",
            "data": [
                {"x": 2000, "y": 22},
                {"x": 2001, "y": 20},
                {"x": 2002, "y": 19},
                {"x": 2003, "y": 18},
                {"x": 2004, "y": 17},
                {"x": 2005, "y": 16},
            ],
        },
        {
            "id": "TypeScript",
            "data": [
                {"x": 2000, "y": 0},
                {"x": 2001, "y": 0},
                {"x": 2002, "y": 2},
                {"x": 2003, "y": 5},
                {"x": 2004, "y": 10},
                {"x": 2005, "y": 18},
            ],
        },
    ]

    return rx.box(
        rx.el.div(
            area_bump_chart(
                data=data,
                margin={"top": 40, "right": 100, "bottom": 40, "left": 100},
                colors={"scheme": "nivo"},
                blend_mode="multiply",
                start_label="id",
                end_label="id",
                axes_bottom_legend="Year",
                axes_left_legend="Usage (%)",
                interpolation="smooth",
                spacing=20,
                border_width=1,
                border_color={"from": "color", "modifiers": [["darker", 0.4]]},
                fill_opacity=0.85,
                is_interactive=True,
            ),
            height="400px",
            width="800px",
        ),
        class_name="size-full flex items-center justify-center align-center overflow-x-scroll",
    )
