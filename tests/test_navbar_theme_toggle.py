"""Regression coverage for the navbar light/dark theme toggle.

The navbar's ``light_and_dark_toggle`` previously bound two independent,
unreconciled toggles to a single click:

    on_click=[rx.toggle_color_mode, rx.call_script(TOGGLE_DARK_JS)]

``rx.toggle_color_mode`` flips Reflex's React ``ColorModeContext`` state (whose
``useEffect`` rewrites ``document.documentElement`` classes last), while
``TOGGLE_DARK_JS`` flips the DOM ``dark`` class, ``localStorage.theme`` and the
``darkmode`` ClientStateVar from the *current* DOM state. The two are never
reconciled: after the ``/create`` sidebar "Menu > Light/Dark" item (which
invokes ``TOGGLE_DARK_JS`` alone) leaves React's color-mode state stale, a
navbar click flips the two sources in opposite directions. The fix is to use
a single source of truth — drop ``rx.toggle_color_mode`` and rely only on
``TOGGLE_DARK_JS`` (matching the sidebar "Light/Dark" item in
``app/templates/options.py``). These tests pin that behaviour so the dual
toggle and the navbar/sidebar divergence cannot be re-introduced.
"""  # noqa: INP001

from reflex_base.components.component import Component
from reflex_base.event import EventChain, EventSpec

from app.templates.navbar import light_and_dark_toggle
from app.templates.options import menu_panel


def _find_button(component: Component) -> Component | None:
    """Depth-first walk for the first ``<button>`` node in a Reflex tree."""
    if getattr(component, "tag", None) == "button":
        return component

    for child in getattr(component, "children", []):
        button = _find_button(child)
        if button is not None:
            return button

    return None


def _find_light_dark_item(component: Component) -> Component | None:
    """Find the ``Select.Item`` whose item text is "Light/Dark" in the Menu panel."""
    pending: list[Component] = [component]
    while pending:
        current = pending.pop()
        if getattr(current, "tag", None) == "Select.Item":
            for child in getattr(current, "children", []):
                if _item_text_is(child, "Light/Dark"):
                    return current
        pending.extend(
            child
            for child in getattr(current, "children", [])
            if hasattr(child, "children")
        )
    return None


def _item_text_is(component: Component, label: str) -> bool:
    if getattr(component, "tag", None) != "Select.ItemText":
        return False
    children = getattr(component, "children", None)
    if not children:
        return False
    return str(children[0]).strip("'\"") == label


def _on_click_chain(component: Component) -> EventChain:
    """Return ``component``'s ``on_click`` chain narrowed to ``EventChain``.

    ``Component.event_triggers`` is annotated ``dict[str, EventChain | Var]``
    (a Var-typed value can be assigned in user code), so strict type checkers
    require a runtime narrowing before ``.events`` can be accessed.
    """
    assert "on_click" in component.event_triggers
    chain = component.event_triggers["on_click"]
    assert isinstance(chain, EventChain)
    return chain


def test_toggle_on_click_is_single_call_script_event() -> None:
    """The on_click handler must fire exactly one ``rx.call_script`` event.

    A two-event chain ``[rx.toggle_color_mode, rx.call_script(TOGGLE_DARK_JS)]``
    is the bug: each event flips an independent source of truth with no
    reconciliation. Exactly one event that is a ``call_script`` ``EventSpec``
    means the navbar uses a single source of truth and can never desync from
    the DOM/localStorage/``darkmode`` state the engine script manages —
    whether the regression takes the form of re-adding the second toggle or
    replacing the call_script with another single event type.
    """
    button = _find_button(light_and_dark_toggle())

    assert button is not None
    chain = _on_click_chain(button)

    assert len(chain.events) == 1
    [event] = chain.events
    assert isinstance(event, EventSpec)
    assert "call_script" in getattr(event.handler.fn, "__qualname__", "")


def test_navbar_toggle_matches_sidebar_light_dark_dispatch() -> None:
    """Navbar and sidebar "Light/Dark" must dispatch through the same toggle.

    The bug report's "codebase inconsistency" is that the navbar used
    ``[rx.toggle_color_mode, rx.call_script(TOGGLE_DARK_JS)]`` while the
    sidebar used ``rx.call_script(TOGGLE_DARK_JS)``. Both controls should
    update the *same* theme state through the *same* single source of truth;
    this test prevents the divergence from returning by sampling the
    sidebar's Light/Dark ``select.item`` and confirming its on_click chain
    also carries exactly one ``call_script`` event over ``TOGGLE_DARK_JS``.
    """
    sidebar_item = _find_light_dark_item(menu_panel(desktop=True))

    assert sidebar_item is not None, (
        "Sidebar Menu panel must contain a 'Light/Dark' item"
    )
    chain = _on_click_chain(sidebar_item)
    rendered = str(sidebar_item)

    assert len(chain.events) == 1
    [event] = chain.events
    assert isinstance(event, EventSpec)
    assert "call_script" in getattr(event.handler.fn, "__qualname__", "")
    for marker in (
        "classList.contains('dark')",
        "localStorage.setItem('theme'",
        "_client_state_setDarkmode",
    ):
        assert marker in rendered, (
            f"Sidebar Light/Dark item missing TOGGLE_DARK_JS marker {marker!r}"
        )
