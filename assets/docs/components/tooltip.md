

# Tooltip

A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.

# Installation

Copy the following code into your app directory.

### CLI

```bash
buridan add component tooltip
```

### Manual Installation

```python
from typing import Literal

from reflex.components.component import Component, ComponentNamespace
from reflex.event import EventHandler, passthrough_event_spec
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var
from reflex_components_core.el import svg

from .core import PACKAGE_NAME, BaseUIComponent, cn

LiteralSide = Literal["top", "right", "bottom", "left", "inline-end", "inline-start"]
LiteralAlign = Literal["start", "center", "end"]
LiteralPositionMethod = Literal["absolute", "fixed"]
LiteralTrackCursorAxis = Literal["none", "bottom", "x", "y"]


class ClassNames:
    TRIGGER = "inline-flex items-center justify-center"
    POPUP = "z-50 inline-flex w-fit max-w-xs origin-(--transform-origin) items-center gap-1.5 rounded-lg bg-foreground px-3 py-1.5 text-xs text-background has-data-[slot=kbd]:pr-1.5 data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 **:data-[slot=kbd]:relative **:data-[slot=kbd]:isolate **:data-[slot=kbd]:z-50 **:data-[slot=kbd]:rounded-sm data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95"
    ARROW = "data-[side=bottom]:top-[-7.5px] data-[side=left]:right-[-12.5px] data-[side=left]:rotate-90 data-[side=right]:left-[-12.5px] data-[side=right]:-rotate-90 data-[side=top]:bottom-[-7.5px] data-[side=top]:rotate-180"


def arrow_svg(class_name: str | Var[str] = "") -> Component:

    return svg(
        svg.path(
            d="M9.66437 2.60207L4.80758 6.97318C4.07308 7.63423 3.11989 8 2.13172 8H0V9H20V8H18.5349C17.5468 8 16.5936 7.63423 15.8591 6.97318L11.0023 2.60207C10.622 2.2598 10.0447 2.25979 9.66437 2.60207Z",
            class_name=cn("fill-foreground", class_name),
        ),
        svg.path(
            d="M10.3333 3.34539L5.47654 7.71648C4.55842 8.54279 3.36693 9 2.13172 9H0V8H2.13172C3.11989 8 4.07308 7.63423 4.80758 6.97318L9.66437 2.60207C10.0447 2.25979 10.622 2.2598 11.0023 2.60207L15.8591 6.97318C16.5936 7.63423 17.5468 8 18.5349 8H20V9H18.5349C17.2998 9 16.1083 8.54278 15.1901 7.71648L10.3333 3.34539Z",
            class_name="fill-none",
        ),
        width="20",
        height="10",
        xmlns="http://www.w3.org/2000/svg",
        custom_attrs={"viewBox": "0 0 20 10"},
        fill="none",
    )


class TooltipBaseComponent(BaseUIComponent):
    library = f"{PACKAGE_NAME}/tooltip"

    @property
    def import_var(self):
        return ImportVar(tag="Tooltip", package_path="", install=False)


class TooltipRoot(TooltipBaseComponent):
    tag = "Tooltip.Root"

    open: Var[bool]

    default_open: Var[bool]

    on_open_change: EventHandler[passthrough_event_spec(bool, dict)]

    on_open_change_complete: EventHandler[passthrough_event_spec(bool)]

    track_cursor_axis: Var[LiteralTrackCursorAxis]

    disabled: Var[bool]

    delay: Var[int]

    close_delay: Var[int]

    hoverable: Var[bool]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "tooltip"
        return super().create(*children, **props)


class TooltipProvider(TooltipBaseComponent):
    tag = "Tooltip.Provider"

    delay: Var[int]

    close_delay: Var[int]

    timeout: Var[int]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "tooltip-provider"
        return super().create(*children, **props)


class TooltipTrigger(TooltipBaseComponent):
    tag = "Tooltip.Trigger"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "tooltip-trigger"
        cls.set_class_name(ClassNames.TRIGGER, props)
        return super().create(*children, **props)


class TooltipPortal(TooltipBaseComponent):
    tag = "Tooltip.Portal"

    container: Var[str]

    keep_mounted: Var[bool]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        ##

        props["data-slot"] = "tooltip-portal"
        return super().create(*children, **props)


class TooltipPositioner(TooltipBaseComponent):
    tag = "Tooltip.Positioner"

    align: Var[LiteralAlign]

    align_offset: Var[int]

    side: Var[LiteralSide]

    side_offset: Var[int]

    arrow_padding: Var[int]

    anchor: Var[str]

    collision_boundary: Var[str]

    collision_padding: Var[int]

    sticky: Var[bool]

    position_method: Var[LiteralPositionMethod]

    track_anchor: Var[bool]

    collision_avoidance: Var[str | dict[str, str]]

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "tooltip-positioner"
        return super().create(*children, **props)


class TooltipPopup(TooltipBaseComponent):
    tag = "Tooltip.Popup"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data_slot"] = "tooltip-popup"
        cls.set_class_name(ClassNames.POPUP, props)
        return super().create(*children, **props)


class TooltipArrow(TooltipBaseComponent):
    tag = "Tooltip.Arrow"

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "tooltip-arrow"
        cls.set_class_name(ClassNames.ARROW, props)

        if not children:
            return super().create(arrow_svg(), **props)

        return super().create(*children, **props)


class Tooltip(ComponentNamespace):
    provider = staticmethod(TooltipProvider.create)
    root = staticmethod(TooltipRoot.create)
    trigger = staticmethod(TooltipTrigger.create)
    portal = staticmethod(TooltipPortal.create)
    positioner = staticmethod(TooltipPositioner.create)
    popup = staticmethod(TooltipPopup.create)
    arrow = staticmethod(TooltipArrow.create)
    class_names = ClassNames


tooltip = Tooltip()
```


# Usage


```python
from components.ui.tooltip import Tooltip
```


# Anatomy 
Use the following composition to build a `Tooltip` component.

> **Error in anatomy: No module named 'app.www.anatomy'**



# Examples


## General

A simple tooltip example. Use the `dealy` prop to change how fast the tootip shows.

```python
def tooltip_general():
    return tooltip.provider(
        tooltip.root(
            tooltip.trigger(
                render_=button("Hover", variant="outline", size="sm"),
            ),
            tooltip.portal(
                tooltip.positioner(
                    tooltip.popup(tooltip.arrow(), "Add to library"),
                ),
            ),
        ),
        delay=0,
    )
```


## Side
Use the `side` prop in `tooltip.positioner()` to change the position of the tooltip.

```python
def tooltip_sides():

    return rx.el.div(
        *[
            tooltip.provider(
                tooltip.root(
                    tooltip.trigger(
                        render_=button(side.capitalize(), variant="outline", size="sm"),
                    ),
                    tooltip.portal(
                        tooltip.positioner(
                            tooltip.popup(tooltip.arrow(), "Add to library"),
                            side=side,
                        ),
                    ),
                ),
                delay=0,
            )
            for side in sides
        ],
        class_name="flex flex-wrap gap-2",
    )
```

