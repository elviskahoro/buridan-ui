import reflex as rx


def not_found_page() -> rx.Component:
    return rx.el.div(  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
        rx.el.div(  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
            rx.el.h1(  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
                "404",
                class_name=(
                    "inline-block mr-5 pr-[23px] text-2xl font-medium align-top "
                    "leading-[49px] border-r border-input"
                ),
            ),
            rx.el.h2(  # pyright: ignore[reportUnknownMemberType]  # reflex component factories are partially unknown
                "This page could not be found.",
                class_name="text-sm font-normal leading-[49px] m-0",
            ),
            class_name="flex flex-row items-center",
        ),
        class_name="w-full h-screen flex items-center justify-center",
    )
