import reflex as rx

from components.ui.tooltip import tooltip


def attach_tooltip(func: rx.Component, label: str) -> rx.Component:
    return tooltip.provider(
        tooltip.root(
            tooltip.trigger(render_=func),
            tooltip.portal(
                tooltip.positioner(
                    tooltip.popup(
                        tooltip.arrow(),
                        label,
                        class_name="rounded-lg",
                    ),
                    side="bottom",
                ),
            ),
        ),
        delay=0,
    )
