from typing import Any, cast

import reflex as rx
from reflex.experimental import ClientStateVar


# Used in --demo(form_state_pattern_example)--
def form_state_pattern_example():
    form_state = ClientStateVar.create("form", {})
    form = cast("Any", form_state.value)

    return rx.el.input(
        value=form.get("username", ""),
        on_change=cast(
            "Any",
            lambda v: form_state.set_value(form.merge({"username": v})),
        ),
    )
