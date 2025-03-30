import reflex as rx


def create_grid_item_chart_section(
    component: rx.Component,
    footer: rx.Component,
    sm_span: int = 1,
    md_span: int = 1,
    lg_span: int = 1,
    padding: int = 0,
) -> rx.Component:
    span_classes = (
        f"col-span-{sm_span} "
        f"sm:col-span-{sm_span} "
        f"md:col-span-{md_span} "
        f"lg:col-span-{lg_span} "
    )

    return rx.box(
        rx.box(
            component,
            border=f"1px solid {rx.color('gray', 4)}",
            class_name=f"{span_classes} p-{padding} rounded-2xl h-full shadow-md z-10",
        ),
        footer,
        class_name=f"{span_classes} p-2 rounded-2xl h-full flex flex-col inset-shadow-sm",
    )


def create_grid_item(
    component: rx.Component,
    sm_span: int = 1,
    md_span: int = 1,
    lg_span: int = 1,
    padding: int = 4,
) -> rx.Component:
    span_classes = (
        f"col-span-{sm_span} "
        f"sm:col-span-{sm_span} "
        f"md:col-span-{md_span} "
        f"lg:col-span-{lg_span} "
    )

    return rx.box(
        rx.box(
            component,
            border=f"1px solid {rx.color('gray', 4)}",
            class_name=f"{span_classes} p-{padding} rounded-lg border-2 border-solid shadow-sm h-full",
        ),
        border=f"1px solid {rx.color('gray', 5)}",
        class_name=f"{span_classes} p-2 rounded-lg shadow-lg h-full",
    )


def responsive_grid(
    *children: rx.Component,
    lg: int = 1,
    md: int = 1,
    sm: int = 1,
    gap: int = 8,
    padding: int = 4,
) -> rx.Component:
    # Generate Tailwind classes for each breakpoint
    breakpoint_classes = (
        f"sm:grid-cols-{sm} "  # Small screens
        f"md:grid-cols-{md} "  # Medium screens
        f"lg:grid-cols-{lg} "  # Large screens
    )

    return rx.grid(
        *children,
        class_name=f"grid grid-cols-1 {breakpoint_classes} gap-{gap} p-{padding} size-full",
    )
