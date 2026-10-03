import reflex as rx

from app.utils.links import external_link


def footer() -> rx.Component:
    return rx.el.p(
        rx.el.span(
            "Built by ",
            external_link(
                "Line Indent",
                href="https://github.com/LineIndent",
                class_name="font-semibold underline",
            ),
            " at ",
            external_link(
                "Reflex",
                href="https://reflex.dev",
                class_name="font-semibold underline",
            ),
            ".",
        ),
        rx.el.span(
            " The source code is available on ",
            external_link(
                "GitHub",
                href="https://github.com/LineIndent/ui",
                class_name="font-semibold underline",
            ),
            ".",
            class_name="block sm:inline",
        ),
        class_name="w-full text-[13px] font-light",
    )
