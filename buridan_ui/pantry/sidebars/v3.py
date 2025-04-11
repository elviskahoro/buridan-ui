import reflex as rx
from reflex.experimental import ClientStateVar


def sidebar_v3():
    # Client state for tracking active item and hovered item
    active_item = ClientStateVar.create("active_item_compact", "Dashboard")
    hover_item = ClientStateVar.create("hover_item", "")

    # Menu items with icons
    menu_items = [
        {"name": "Dashboard", "icon": "layout-dashboard"},
        {"name": "Users", "icon": "users"},
        {"name": "Messages", "icon": "mail"},
        {"name": "Analytics", "icon": "bar-chart-2"},
        {"name": "Calendar", "icon": "calendar"},
        {"name": "Files", "icon": "file"},
        {"name": "Tasks", "icon": "check-square"},
        {"name": "Settings", "icon": "settings"},
    ]

    # Create menu item with tooltip
    def create_compact_item(item):
        return rx.tooltip(
            rx.box(
                rx.icon(
                    tag=item["icon"],
                    color=rx.cond(
                        active_item.value == item["name"],
                        rx.color("blue", 9),
                        rx.color("slate", 11),
                    ),
                    size=14,
                ),
                width="48px",
                height="48px",
                display="flex",
                align_items="center",
                justify_content="center",
                border_radius="md",
                bg=rx.cond(
                    active_item.value == item["name"],
                    rx.color("blue", 1),
                    "transparent",
                ),
                border_left=rx.cond(
                    active_item.value == item["name"],
                    f"3px solid {rx.color('blue', 9)}",
                    "3px solid transparent",
                ),
                _hover={"bg": rx.color("gray", 2)},
                cursor="pointer",
                on_click=active_item.set_value(item["name"]),
                on_mouse_enter=hover_item.set_value(item["name"]),
                on_mouse_leave=hover_item.set_value(""),
            ),
            content=item["name"],
            placement="right",
        )

    # Main content
    content = rx.vstack(
        active_item,
        hover_item,
        rx.vstack(
            rx.box(
                rx.heading("AD", size="3"),
                padding="12px 0",
                width="100%",
                text_align="center",
            ),
            rx.divider(),
            *[create_compact_item(item) for item in menu_items],
            spacing="2",
            width="100%",
            padding="16px 0",
            align_items="center",
        ),
        height="100%",
        width="100%",
        padding="0",
        align_items="center",
    )

    # Return the sidebar
    return rx.box(
        content,
        height="100vh",
        width="64px",
        border_right=f"1px solid {rx.color('gray', 4)}",
        bg=rx.color("gray", 1),
        overflow_y="auto",
    )
