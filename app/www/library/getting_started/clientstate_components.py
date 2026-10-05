import reflex as rx
from reflex.experimental import ClientStateVar


# Used in --demo(form_state_pattern_example)--
def form_state_pattern_example():
    form_state = ClientStateVar.create("form", {})

    return rx.input(
        value=form_state.value.get("username", ""),
        on_change=lambda v: form_state.set_value(
            form_state.value.merge({"username": v})
        ),
    )
