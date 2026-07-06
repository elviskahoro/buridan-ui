

# Select
Displays a list of options for the user to pick from—triggered by a button.

# Installation
Copy the following code into your app directory.

### CLI

```bash
buridan add component select
```

### Manual Installation

```python
from typing import Any, Literal

from reflex.components.component import Component, ComponentNamespace
from reflex.event import EventHandler, passthrough_event_spec
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var
from reflex_components_core.core.foreach import foreach as foreach

from ..icons.hugeicon import hi
from .core import PACKAGE_NAME, BaseUIComponent

LiteralSelectSize = Literal["xs", "sm", "md", "lg", "xl"]
LiteralAlign = Literal["start", "center", "end"]
LiteralSide = Literal["bottom", "inline-end", "inline-start", "left", "right", "top"]
LiteralPosition = Literal["absolute", "fixed"]
LiteralOrientation = Literal["horizontal", "vertical"]


class ClassNames:
    TRIGGER = "flex w-fit items-center justify-between gap-1.5 rounded-lg border border-input bg-transparent py-2 pr-2 pl-2.5 text-sm whitespace-nowrap transition-colors outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 data-placeholder:text-muted-foreground data-[size=default]:h-8 data-[size=sm]:h-7 data-[size=sm]:rounded-[min(var(--radius-md),10px)] *:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-1.5 dark:bg-input/30 dark:hover:bg-input/50 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4"
    VALUE = "flex-1 text-left cursor-default"
    ICON = "flex size-4 text-secondary-10 group-data-[disabled]/trigger:text-current"
    POPUP = "relative isolate z-50 max-h-(--available-height) w-(--anchor-width) min-w-36 origin-(--transform-origin) overflow-x-hidden overflow-y-auto rounded-lg bg-popover text-popover-foreground shadow-md ring-1 ring-foreground/10 duration-100 data-[align-trigger=true]:animate-none data-[side=bottom]:slide-in-from-top-2 data-[side=inline-end]:slide-in-from-left-2 data-[side=inline-start]:slide-in-from-right-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95"
    ITEM = "focus:bg-accent focus:text-accent-foreground [&_svg:not([class*='text-'])]:text-muted-foreground relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 px-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 *:[span]:last:flex *:[span]:last:items-center *:[span]:last:gap-2"
    ITEM_INDICATOR = ""
    ITEM_TEXT = "text-start"
    GROUP = "p-1"
    GROUP_LABEL = "text-muted-foreground px-2 py-1.5 text-xs"
    SEPARATOR = "bg-border pointer-events-none -mx-1 my-1 h-px"
    ARROW = "data-[side=bottom]:top-[-8px] data-[side=left]:right-[-13px] data-[side=left]:rotate-90 data-[side=right]:left-[-13px] data-[side=right]:-rotate-90 data-[side=top]:bottom-[-8px] data-[side=top]:rotate-180"
    POSITIONER = "outline-none"
    SCROLL_ARROW_UP = "top-0 z-10 flex w-full cursor-default items-center justify-center bg-popover py-1"
    SCROLL_ARROW_DOWN = "bottom-0 z-10 flex w-full cursor-default items-center justify-center bg-popover py-1"


class SelectBaseComponent(BaseUIComponent):
    library = f"{PACKAGE_NAME}/select"

    @property
    def import_var(self):
        return ImportVar(tag="Select", package_path="", install=False)


class SelectRoot(SelectBaseComponent):
    tag = "Select.Root"

    name: Var[str]

    default_value: Var[Any]

    value: Var[Any]

    on_value_change: EventHandler[passthrough_event_spec(str)]

    default_open: Var[bool]

    open: Var[bool]

    on_open_change: EventHandler[passthrough_event_spec(bool)]

    actions_ref: Var[str]

    is_item_equal_to_value: Var[Any]

    item_to_string_label: Var[Any]

    item_to_string_value: Var[Any]

    items: Var[Any]

    modal: Var[bool]

    multiple: Var[bool]

    on_open_change_complete: EventHandler[passthrough_event_spec(bool)]

    disabled: Var[bool]

    read_only: Var[bool]

    required: Var[bool]

    input_ref: Var[Any]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "select"
        return super().create(*children, **props)


class SelectTrigger(SelectBaseComponent):
    tag = "Select.Trigger"

    disabled: Var[bool]

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-trigger"

        size = props.pop("size", "default")

        props["data_size"] = size

        cls.set_class_name(ClassNames.TRIGGER, props)
        return super().create(*children, **props)


class SelectValue(SelectBaseComponent):
    tag = "Select.Value"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-value"
        cls.set_class_name(ClassNames.VALUE, props)
        return super().create(*children, **props)


class SelectBackdrop(SelectBaseComponent):
    tag = "Select.Backdrop"

    render_: Var[Component]


class SelectPortal(SelectBaseComponent):
    tag = "Select.Portal"

    container: Var[str]


class SelectPositioner(SelectBaseComponent):
    tag = "Select.Positioner"

    align: Var[LiteralAlign]

    align_offset: Var[int]

    side: Var[LiteralSide]

    arrow_padding: Var[int]

    collision_padding: Var[int | list[int]]

    sticky: Var[bool]

    position_method: Var[LiteralPosition]

    align_item_with_trigger: Var[bool] = Var.create(False)

    track_anchor: Var[bool]

    side_offset: Var[int]

    collision_avoidance: Var[str]

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-positioner"
        props.setdefault("side_offset", 4)
        cls.set_class_name(ClassNames.POSITIONER, props)
        return super().create(*children, **props)


class SelectPopup(SelectBaseComponent):
    tag = "Select.Popup"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-popup"
        cls.set_class_name(ClassNames.POPUP, props)
        return super().create(*children, **props)


class SelectList(SelectBaseComponent):
    tag = "Select.List"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-list"
        return super().create(*children, **props)


class SelectItem(SelectBaseComponent):
    tag = "Select.Item"

    label: Var[str]

    value: Var[Any]

    disabled: Var[bool]

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-item"
        cls.set_class_name(ClassNames.ITEM, props)
        return super().create(*children, **props)


class SelectItemText(SelectBaseComponent):
    tag = "Select.ItemText"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-item-text"
        cls.set_class_name(ClassNames.ITEM_TEXT, props)
        return super().create(*children, **props)


class SelectItemIndicator(SelectBaseComponent):
    tag = "Select.ItemIndicator"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props):
        props["data-slot"] = "select-item-indicator"
        cls.set_class_name(ClassNames.ITEM_INDICATOR, props)

        if not children:
            children = (hi("Tick02Icon", class_name="size-4 text-secondary-10"),)

        return super().create(*children, **props)


class SelectGroup(SelectBaseComponent):
    tag = "Select.Group"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-group"
        cls.set_class_name(ClassNames.GROUP, props)
        return super().create(*children, **props)


class SelectGroupLabel(SelectBaseComponent):
    tag = "Select.GroupLabel"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-group-label"
        cls.set_class_name(ClassNames.GROUP_LABEL, props)
        return super().create(*children, **props)


class SelectSeparator(SelectBaseComponent):
    tag = "Select.Separator"

    orientation: Var[LiteralOrientation] = Var.create("horizontal")

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-separator"
        cls.set_class_name(ClassNames.SEPARATOR, props)
        return super().create(*children, **props)


class SelectIcon(SelectBaseComponent):
    tag = "Select.Icon"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props):
        props["data-slot"] = "select-icon"
        cls.set_class_name(ClassNames.ICON, props)

        if not children:
            children = (hi("ArrowDown01Icon", class_name="size-4"),)

        return super().create(*children, **props)


class SelectArrow(SelectBaseComponent):
    tag = "Select.Arrow"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-arrow"
        cls.set_class_name(ClassNames.ARROW, props)
        return super().create(*children, **props)


class SelectScrollUpArrow(SelectBaseComponent):
    tag = "Select.ScrollUpArrow"

    keep_mounted: Var[bool]

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-scroll-up-arrow"
        cls.set_class_name(ClassNames.SCROLL_ARROW_UP, props)

        if "render_" not in props or props["render_"] is None:
            props["render_"] = hi("ArrowUp01Icon", class_name="size-6")

        return super().create(*children, **props)


class SelectScrollDownArrow(SelectBaseComponent):
    tag = "Select.ScrollDownArrow"

    keep_mounted: Var[bool]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:

        props["data-slot"] = "select-scroll-down-arrow"
        cls.set_class_name(ClassNames.SCROLL_ARROW_DOWN, props)

        if "render_" not in props or props["render_"] is None:
            props["render_"] = hi("ArrowDown01Icon", class_name="size-6")

        return super().create(*children, **props)


class Select(ComponentNamespace):
    root = staticmethod(SelectRoot.create)
    trigger = staticmethod(SelectTrigger.create)
    value = staticmethod(SelectValue.create)
    icon = staticmethod(SelectIcon.create)
    backdrop = staticmethod(SelectBackdrop.create)
    portal = staticmethod(SelectPortal.create)
    positioner = staticmethod(SelectPositioner.create)
    popup = staticmethod(SelectPopup.create)
    arrow = staticmethod(SelectArrow.create)
    scroll_up_arrow = staticmethod(SelectScrollUpArrow.create)
    scroll_down_arrow = staticmethod(SelectScrollDownArrow.create)
    list = staticmethod(SelectList.create)
    item = staticmethod(SelectItem.create)
    item_text = staticmethod(SelectItemText.create)
    item_indicator = staticmethod(SelectItemIndicator.create)
    group = staticmethod(SelectGroup.create)
    group_label = staticmethod(SelectGroupLabel.create)
    separator = staticmethod(SelectSeparator.create)
    class_names = ClassNames


select = Select()
```


# Usage

```python
from components.ui.select import Select
```


# Anatomy 
Use the following composition to build a `Select` component.

> **Error in anatomy: No module named 'app.www.anatomy'**


# Examples

## Align Item
Use `align_item_with_trigger` on `select.positioner()` to control whether the selected item aligns with the trigger. When true (default), the popup positions so the selected item appears over the trigger. When false, the popup aligns to the trigger edge.


```python
def select_align_with_items():

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p("Align Item", class_name="font-medium text-foreground"),
                rx.el.p(
                    "Toggle to align the item with the trigger.",
                    class_name="text-muted-foreground",
                ),
                class_name="flex flex-col gap-y-2 text-sm",
            ),
            switch.root(
                switch.thumb(),
                on_checked_change=align_with_item_trigger.set_value(
                    ~align_with_item_trigger.value
                ),
            ),
            class_name="flex flex-row items-start justify-between w-full",
        ),
        select.root(
            select.trigger(
                select.value(),
                select.icon(hi("ArrowDown01Icon", classs_name="size-4")),
                class_name="w-full flex items-center justify-between group",
            ),
            select.portal(
                select.positioner(
                    select.popup(
                        select.group(
                            select.group_label("Fruit"),
                            *[
                                select.item(
                                    select.item_text(fruit.capitalize()),
                                    select.item_indicator(
                                        hi("Tick02Icon", class_name="size-4")
                                    ),
                                    value=fruit,
                                    class_name="w-full !max-w-sm flex flex-row items-center justify-between",
                                )
                                for fruit in items
                            ],
                        ),
                    ),
                    side_offset=4,
                    align_item_with_trigger=align_with_item_trigger.value,
                ),
            ),
            name="example_select",
            default_value="blueberry",
        ),
        class_name="flex flex-col gap-y-4 max-w-sm",
    )
```


## Groups
Use `select.group` to organize items into sections, `select.group_label` to label each section, and `select.separator` to visually divide groups.


```python
def select_groups():
    fruits = [
        {"label": "Apple", "value": "apple"},
        {"label": "Banana", "value": "banana"},
        {"label": "Blueberry", "value": "blueberry"},
    ]

    vegetables = [
        {"label": "Carrot", "value": "carrot"},
        {"label": "Broccoli", "value": "broccoli"},
        {"label": "Spinach", "value": "spinach"},
    ]

    return select.root(
        select.trigger(
            select.value(),
            select.icon(),
            class_name="w-full max-w-48 flex items-center justify-between",
        ),
        select.portal(
            select.positioner(
                select.popup(
                    select.group(
                        select.group_label("Fruits"),
                        *[
                            select.item(
                                select.item_text(item["label"]),
                                select.item_indicator(),
                                value=item["value"],
                                class_name="flex flex-row items-center justify-between",
                            )
                            for item in fruits
                        ],
                    ),
                    select.separator(),
                    select.group(
                        select.group_label("Vegetables"),
                        *[
                            select.item(
                                select.item_text(item["label"]),
                                select.item_indicator(),
                                value=item["value"],
                                class_name="flex flex-row items-center justify-between",
                            )
                            for item in vegetables
                        ],
                    ),
                ),
            ),
        ),
        items=[*fruits, *vegetables],
        name="select_groups",
        default_value="banana",
    )
```


## Scrollable
Use `select.scroll_up_arrow` and `select.scroll_down_arrow` to provide navigation controls for scrolling through long lists of select items within the dropdown.


```python
def select_with_scroll_arrows():
    north_america = [
        {"label": "Eastern Standard Time", "value": "est"},
        {"label": "Central Standard Time", "value": "cst"},
        {"label": "Mountain Standard Time", "value": "mst"},
        {"label": "Pacific Standard Time", "value": "pst"},
        {"label": "Alaska Standard Time", "value": "akst"},
        {"label": "Hawaii Standard Time", "value": "hst"},
    ]

    europe_africa = [
        {"label": "Greenwich Mean Time", "value": "gmt"},
        {"label": "Central European Time", "value": "cet"},
        {"label": "Eastern European Time", "value": "eet"},
        {"label": "Central Africa Time", "value": "cat"},
        {"label": "East Africa Time", "value": "eat"},
    ]

    asia = [
        {"label": "Moscow Time", "value": "msk"},
        {"label": "India Standard Time", "value": "ist"},
        {"label": "China Standard Time", "value": "cst_china"},
        {"label": "Japan Standard Time", "value": "jst"},
    ]

    return select.root(
        select.trigger(
            select.value(),
            select.icon(),
            class_name="w-full max-w-64 flex items-center justify-between",
        ),
        select.portal(
            select.positioner(
                select.popup(
                    select.scroll_up_arrow(),
                    select.list(
                        select.group(
                            select.group_label("North America"),
                            *[
                                select.item(
                                    select.item_text(i["label"]),
                                    select.item_indicator(),
                                    value=i["value"],
                                )
                                for i in north_america
                            ],
                        ),
                        select.group(
                            select.group_label("Europe & Africa"),
                            *[
                                select.item(
                                    select.item_text(i["label"]),
                                    select.item_indicator(),
                                    value=i["value"],
                                )
                                for i in europe_africa
                            ],
                        ),
                        select.group(
                            select.group_label("Asia"),
                            *[
                                select.item(
                                    select.item_text(i["label"]),
                                    select.item_indicator(),
                                    value=i["value"],
                                )
                                for i in asia
                            ],
                        ),
                        class_name="max-h-64 overflow-y-auto",
                    ),
                    select.scroll_down_arrow(),
                ),
            ),
        ),
        items=[
            {"label": "Select timezone", "value": None},
            *north_america,
            *europe_africa,
            *asia,
        ],
        name="timezone_select",
        default_value="est",
    )
```

