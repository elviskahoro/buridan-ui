import reflex as rx
from buridan_ui.wrappers.base.main import base


def wrapper(title: str, instructions: str, components=None, **kwargs):
    if components is None:
        components = []
    return rx.hstack(
        rx.vstack(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        title,
                        size="1",
                        weight="bold",
                        color=rx.color("slate", 11),
                    ),
                    align="center",
                ),
                rx.text(
                    instructions,
                    size="2",
                    weight="regular",
                    color=rx.color("slate", 12),
                ),
                width="100%",
                spacing="1",
            ),
            *components,
            width="100%",
        ),
        width="100%",
        align="start",
        justify="start",
        # padding_left="15px",
        border_radius="0px 5px 5px 0px",
        **kwargs,
    )


def create_code_line(code_string: str, _tag_id: str):
    return rx.hstack(
        rx.code_block(
            code_string,
            width="100%",
            font_size="12px",
            language="bash",
            # theme=Theme.darcula,
            wrap_long_lines=True,
            scrollbar_width="none",
            code_tag_props={"pre": "transparent", "bg": "transparent"},
            custom_attrs={"bg": "transparent"},
            bg="transparent",
            class_name="rounded-md shadow-sm",
            border=f"0.81px solid {rx.color('gray', 4)}",
        ),
        rx.el.button(
            rx.icon(tag="copy", size=13, id=_tag_id),
            cursor="pointer",
            position="absolute",
            right="2%",
            on_click=[
                rx.toast("Command copied"),
                rx.set_clipboard(code_string),
            ],
        ),
        width="100%",
        align="center",
        position="relative",
    )


@base("/getting-started/installation", "Installation")
def installation():
    return [
        rx.box(
            rx.vstack(
                wrapper(
                    "Step 1: Check your Python version",
                    "To use Reflex you need to have Python version 3.9 or above installed on your system.",
                    [create_code_line("python3 --version", "tag-1")],
                ),
                wrapper(
                    "Step 2: PIP install the Reflex framework",
                    "Use the following command to install Reflex:",
                    [
                        create_code_line("pip3 install reflex", "tag-2"),
                        rx.text(
                            "Male sure the latest version of Reflex is installed",
                            size="2",
                            weight="regular",
                            color=rx.color("slate", 12),
                        ),
                        create_code_line("reflex --version", "tag-3"),
                    ],
                ),
                wrapper(
                    "Step 3: Create a new Reflex Web Application",
                    "Inside your root directory, run the following command to create a new app:",
                    [create_code_line("reflex init", "tag-4")],
                ),
                wrapper(
                    "Step 4: Copy & paste a pantry item directly into your app",
                    "You can now easily integrate pantry pantry within your app and personalize them.",
                ),
                width="100%",
                spacing="6",
                position="relative",
            ),
            width="100%",
            display="flex",
            justify_content="start",
            class_name="p-4",
        )
    ]
