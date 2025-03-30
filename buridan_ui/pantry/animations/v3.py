import reflex as rx
from reflex.experimental import ClientStateVar

PASSIVE: dict = {"top": "-20px", "left": "-20px", "opacity": "0"}
ACTIVE: dict = {"top": "-20px", "left": "0px", "opacity": "1"}


# class Animation(rx.State):
#     value: str
#     position: dict = PASSIVE
#
#     async def run_animation(self, new_value: str):
#         self.value = new_value
#
#         if len(self.value) >= 1:
#             self.position = ACTIVE
#             yield
#
#         if len(self.value) == 0:
#             self.position = PASSIVE
#             yield


email = ClientStateVar.create("email", "")
email_label = ClientStateVar.create("email_label", PASSIVE)


def animation_v3():
    return rx.center(
        rx.form(
            rx.input(
                # value=email.value,
                placeholder="Email Address",
                variant="surface",
                color_scheme="gray",
                width="100%",
                # on_change=lambda value: email.set_value(value),
            ),
            rx.text(
                "Email Address",
                size="1",
                color=rx.color("slate", 11),
                position="absolute",
                transition="all 150ms ease",
                style=email_label.value,
            ),
            position="relative",
            max_width="15em",
            width="100%",
        ),
        width="100%",
        height="20em",
    )
