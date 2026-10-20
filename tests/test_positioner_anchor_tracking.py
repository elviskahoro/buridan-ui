# noqa: INP001
"""Regression tests for the anchor-tracking prop on the Base UI positioners.

The pinned ``@base-ui/react`` library renamed ``trackAnchor`` (beta.4) to the
inverted-polarity ``disableAnchorTracking`` (beta.5+, used by 1.6.0). The
Python wrappers must expose the renamed prop so Reflex camelCases it to
``disableAnchorTracking`` and forwards it as a real JSX prop instead of
silently dropping it and leaking ``trackAnchor`` onto the rendered DOM.
"""

import pytest
from reflex.components.component import Component

from components.ui.context_menu import ContextMenuPositioner
from components.ui.menu import MenuPositioner
from components.ui.popover import PopoverPositioner
from components.ui.select import SelectPositioner
from components.ui.tooltip import TooltipPositioner

# (class, id). Sorted by id for stable pytest -v output.
POSITIONERS: list[tuple[type[Component], str]] = [
    (ContextMenuPositioner, "ContextMenuPositioner"),
    (MenuPositioner, "MenuPositioner"),
    (PopoverPositioner, "PopoverPositioner"),
    (SelectPositioner, "SelectPositioner"),
    (TooltipPositioner, "TooltipPositioner"),
]

POSITIONER_IDS = [label for _, label in POSITIONERS]
EXPECTED_POSITIONER_COUNT = 5


def _rendered_props(cls: type[Component], **props: object) -> str:
    """Build a positioner of ``cls`` with ``props`` and return its JSX props as
    the rendered space-joined string used throughout this repo's test suite.
    """
    positioner = cls.create(**props)
    return " ".join(positioner.render()["props"])


@pytest.mark.parametrize(  # pyright: ignore[reportUntypedFunctionDecorator]
    "positioner_cls",
    [cls for cls, _ in POSITIONERS],
    ids=POSITIONER_IDS,
)
def test_positioner_declares_disable_anchor_tracking_and_drops_track_anchor(
    positioner_cls: type[Component],
) -> None:
    """The renamed prop is the only anchor-tracking Var on each positioner."""
    assert hasattr(positioner_cls, "disable_anchor_tracking")
    assert not hasattr(positioner_cls, "track_anchor")


@pytest.mark.parametrize(  # pyright: ignore[reportUntypedFunctionDecorator]
    "positioner_cls",
    [cls for cls, _ in POSITIONERS],
    ids=POSITIONER_IDS,
)
def test_positioner_default_renders_neither_track_anchor_nor_disable_anchor_tracking(
    positioner_cls: type[Component],
) -> None:
    """No caller-supplied value means neither prop should reach the DOM."""
    rendered = _rendered_props(positioner_cls)

    assert "trackAnchor" not in rendered
    assert "disableAnchorTracking" not in rendered


@pytest.mark.parametrize(  # pyright: ignore[reportUntypedFunctionDecorator]
    "positioner_cls",
    [cls for cls, _ in POSITIONERS],
    ids=POSITIONER_IDS,
)
def test_positioner_disable_anchor_tracking_true_forwards_as_jsx_prop(
    positioner_cls: type[Component],
) -> None:
    """``disable_anchor_tracking=True`` must camelCase to the JSX prop
    ``disableAnchorTracking`` and reach Base UI as a top-level prop (not be
    dropped, not be re-routed to ``css``). Mirrors the old ``track_anchor=False``
    "stop tracking the anchor" semantics.
    """
    rendered = _rendered_props(positioner_cls, disable_anchor_tracking=True)

    assert "disableAnchorTracking:true" in rendered
    assert "trackAnchor" not in rendered


@pytest.mark.parametrize(  # pyright: ignore[reportUntypedFunctionDecorator]
    "positioner_cls",
    [cls for cls, _ in POSITIONERS],
    ids=POSITIONER_IDS,
)
def test_positioner_disable_anchor_tracking_false_forwards_as_jsx_prop(
    positioner_cls: type[Component],
) -> None:
    """``disable_anchor_tracking=False`` must forward as ``disableAnchorTracking:false``;
    polarity is preserved so the Base UI default (tracking enabled) survives
    an explicit False.
    """
    rendered = _rendered_props(positioner_cls, disable_anchor_tracking=False)

    assert "disableAnchorTracking:false" in rendered
    assert "trackAnchor" not in rendered


@pytest.mark.parametrize(  # pyright: ignore[reportUntypedFunctionDecorator]
    "positioner_cls",
    [cls for cls, _ in POSITIONERS],
    ids=POSITIONER_IDS,
)
def test_positioner_legacy_track_anchor_no_longer_leaks_to_dom(
    positioner_cls: type[Component],
) -> None:
    """A caller still passing the pre-rename ``track_anchor`` must no longer get
    ``trackAnchor`` as an unknown JSX prop on the rendered ``<div>`` (the exact
    leak that produced React dev warnings before the fix). The legacy name is
    not a declared Var anymore, so it is re-routed to Reflex's ``css`` custom-attrs
    payload rather than reaching the JSX prop list.
    """
    positioner = positioner_cls.create(track_anchor=True)
    props = positioner.render()["props"]

    # No element of the rendered prop list may be a top-level `trackAnchor:...`
    # JSX prop (which is what the original bug produced).
    assert not any(prop.startswith("trackAnchor:") for prop in props)


def test_all_five_positioner_wrappers_are_covered() -> None:
    """Guard against silently adding a sixth positioner without updating this
    regression file. If a new ``*.Positioner`` wrapper is added to
    ``components/ui`` that passes through anchor-positioning, extend
    ``POSITIONERS`` and the new wrapper's own ``test_<component>.py``.
    """
    assert {cls for cls, _ in POSITIONERS} == {
        ContextMenuPositioner,
        MenuPositioner,
        PopoverPositioner,
        SelectPositioner,
        TooltipPositioner,
    }
    assert len(POSITIONERS) == EXPECTED_POSITIONER_COUNT
