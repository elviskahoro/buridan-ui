import reflex as rx
from reflex.experimental import ClientStateVar


def sidebar_v2():
    # Client state for tracking active item
    active_item = ClientStateVar.create("active_item_icons", "Dashboard")

    # Menu items with icons
    menu_items = [
        {"name": "Dashboard", "icon": "layout-dashboard"},
        {"name": "Users", "icon": "users"},
        {"name": "Analytics", "icon": "bar-chart-2"},
        {"name": "Projects", "icon": "folder"},
        {"name": "Tasks", "icon": "check-square"},
        {"name": "Messages", "icon": "mail"},
        {"name": "Settings", "icon": "settings"},
        {"name": "Help", "icon": "help-circle"},
    ]

    def create_menu_item(item):
        return rx.hstack(
            rx.icon(
                tag=item["icon"],
                color=rx.cond(
                    active_item.value == item["name"],
                    rx.color("indigo", 9),
                    rx.color("gray", 9),
                ),
                size=13,
            ),
            rx.text(
                item["name"],
                color=rx.cond(
                    active_item.value == item["name"],
                    rx.color("indigo", 9),
                    rx.color("gray", 11),
                ),
                size="2",
                font_weight=rx.cond(
                    active_item.value == item["name"], "medium", "normal"
                ),
            ),
            spacing="3",
            width="100%",
            border_radius="md",
            padding="10px 16px",
            bg=rx.cond(
                active_item.value == item["name"], rx.color("indigo", 1), "transparent"
            ),
            _hover={"bg": rx.color("gray", 2)},
            cursor="pointer",
            on_click=active_item.set_value(item["name"]),
        )

    # Main content
    content = rx.vstack(
        active_item,
        rx.heading("AdminPanel", size="3", mb="6"),
        rx.vstack(
            *[create_menu_item(item) for item in menu_items],
            spacing="1",
            width="100%",
        ),
        height="100%",
        width="100%",
        padding="24px 16px",
        align_items="flex-start",
    )

    # Return the sidebar
    return rx.box(
        content,
        height="100vh",
        width="260px",
        border_right=f"1px solid {rx.color('gray', 4)}",
        bg=rx.color("gray", 1),
        overflow_y="auto",
    )
