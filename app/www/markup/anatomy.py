import reflex as rx


def render_anatomy_block(src: str) -> rx.Component:
    return rx.el.div(
        rx.el.code(
            src,
            style={
                "white-space": "pre",
                "color": "var(--foreground)",
                "font-size": "13px",
                "padding": "1rem 0.75rem",
                "display": "block",
            },
        ),
        class_name="overflow-x-auto overflow-y-auto scrollbar-none w-full mt-4 mb-8 rounded-[1rem] outline outline-input flex-1 min-h-0 flex flex-col bg-secondary dark:bg-card",
    )
