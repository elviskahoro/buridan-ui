import reflex as rx
from buridan_ui.wrappers.base.main import base


def label(text, add_ons: str = ""):
    return rx.el.label(
        text,
        class_name=f"text-[14px] font-regular {add_ons}",
        color=rx.color("slate", 11),
    )


def text_wrapper(title: str, description: str):
    return rx.el.div(
        rx.el.label(title, class_name="text-md font-bold"),
        rx.el.label(
            description,
            class_name="text-[14px] font-regular",
            color=rx.color("slate", 11),
        ),
        class_name="flex flex-col gap-y-2",
    )


def text_wrapper_open(title: str, component):
    return rx.el.div(
        rx.el.label(title, class_name="text-md font-bold"),
        *component,
        class_name="flex flex-col gap-y-2 w-full",
    )


@base("/getting-started/flexgen", "Flexgen")
def flexgen():
    return [
        rx.box(
            rx.vstack(
                text_wrapper_open(
                    "Flexgen: AI Data App Generator",
                    [
                        label(
                            "Over the upcoming release iterations, Buridan UI components, namely charts and tables, will be integrated into Flexgen, Reflex's AI-powered platform. This will enable users to seamlessly edit, customize, and fine-tune their Buridan UI components with ease. With Flexgen, users will be able to generate dynamic, data-driven charts and tables tailored to their specific needs, empowering developers and designers to rapidly create fully functional and visually appealing UIs without needing deep technical expertise."
                        ),
                        rx.el.div(
                            label(
                                "To use ",
                            ),
                            rx.link(
                                "Flexgen",
                                class_name="underline",
                                href="https://rxbuild.reflex.run/",
                            ),
                            label(
                                " you need to be a Pro user. Sign up now to get early access and build beutifull, hhighly customizable data applications."
                            ),
                        ),
                    ],
                ),
                width="100%",
                spacing="6",
            ),
            width="100%",
            display="flex",
            justify_content="start",
            class_name="p-4",
        )
    ]
