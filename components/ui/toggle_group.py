from typing import Literal

from reflex.components.component import Component, ComponentNamespace
from reflex.event import EventHandler, passthrough_event_spec
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var

from .core import PACKAGE_NAME, BaseUIComponent, cn

LiteralOrientation = Literal["horizontal", "vertical"]
LiteralToggleVariant = Literal["default", "outline"]
LiteralToggleSize = Literal["default", "sm", "lg"]


class ClassNames:
    ROOT = (
        "group/toggle-group flex w-fit flex-row items-center rounded-lg "
        "data-[size=sm]:rounded-[min(var(--radius-md),10px)] "
        "data-[orientation=vertical]:flex-col data-[orientation=vertical]:items-stretch"
    )

    ITEM_VARIANTS = {
        "default": "group-data-[variant=default]/toggle-group:bg-transparent",
        "outline": (
            "group-data-[variant=outline]/toggle-group:border "
            "group-data-[variant=outline]/toggle-group:border-input "
            "group-data-[variant=outline]/toggle-group:bg-transparent "
            "group-data-[variant=outline]/toggle-group:hover:bg-muted"
        ),
    }

    ITEM_SIZES = {
        "default": (
            "group-data-[size=default]/toggle-group:h-8 "
            "group-data-[size=default]/toggle-group:min-w-8 "
            "group-data-[size=default]/toggle-group:px-2.5"
        ),
        "sm": (
            "group-data-[size=sm]/toggle-group:h-7 "
            "group-data-[size=sm]/toggle-group:min-w-7 "
            "group-data-[size=sm]/toggle-group:rounded-[min(var(--radius-md),10px)] "
            "group-data-[size=sm]/toggle-group:px-2.5 "
            "group-data-[size=sm]/toggle-group:text-[0.8rem] "
            "group-data-[size=sm]/toggle-group:[&_svg:not([class*='size-'])]:size-3.5"
        ),
        "lg": (
            "group-data-[size=lg]/toggle-group:h-9 "
            "group-data-[size=lg]/toggle-group:min-w-9 "
            "group-data-[size=lg]/toggle-group:px-2.5"
        ),
    }

    ITEM_BASE = (
        "inline-flex shrink-0 items-center justify-center gap-1 rounded-lg "
        "text-sm font-medium whitespace-nowrap transition-all outline-none "
        "hover:bg-muted hover:text-foreground "
        "focus:z-10 focus-visible:z-10 "
        "focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 "
        "disabled:pointer-events-none disabled:opacity-50 "
        "aria-invalid:border-destructive aria-invalid:ring-destructive/20 "
        "aria-pressed:bg-muted data-[state=on]:bg-muted "
        "dark:aria-invalid:ring-destructive/40 "
        "[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 "
        "group-data-[spacing=0]/toggle-group:rounded-none "
        "group-data-[spacing=0]/toggle-group:px-2 "
        "group-data-[orientation=horizontal]/toggle-group:group-data-[spacing=0]/toggle-group:first:rounded-l-lg "
        "group-data-[orientation=horizontal]/toggle-group:group-data-[spacing=0]/toggle-group:last:rounded-r-lg "
        "group-data-[orientation=vertical]/toggle-group:group-data-[spacing=0]/toggle-group:first:rounded-t-lg "
        "group-data-[orientation=vertical]/toggle-group:group-data-[spacing=0]/toggle-group:last:rounded-b-lg "
        "group-data-[orientation=horizontal]/toggle-group:group-data-[spacing=0]/toggle-group:group-data-[variant=outline]/toggle-group:border-l-0 "
        "group-data-[orientation=horizontal]/toggle-group:group-data-[spacing=0]/toggle-group:group-data-[variant=outline]/toggle-group:first:border-l "
        "group-data-[orientation=vertical]/toggle-group:group-data-[spacing=0]/toggle-group:group-data-[variant=outline]/toggle-group:border-t-0 "
        "group-data-[orientation=vertical]/toggle-group:group-data-[spacing=0]/toggle-group:group-data-[variant=outline]/toggle-group:first:border-t"
    )


class ToggleGroupBaseComponent(BaseUIComponent):
    library = f"{PACKAGE_NAME}/toggle-group"

    @property
    def import_var(self):
        return ImportVar(tag="ToggleGroup", package_path="", install=False)


class ToggleGroupRoot(ToggleGroupBaseComponent):
    tag = "ToggleGroup"
    default_value: Var[list[str | int]]
    value: Var[list[str | int]]
    on_value_change: EventHandler[passthrough_event_spec(list[str | int], dict)]
    multiple: Var[bool]
    disabled: Var[bool]
    loop: Var[bool]
    orientation: Var[LiteralOrientation]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        variant = props.pop("variant", "default")
        size = props.pop("size", "default")
        spacing = props.pop("spacing", 2)
        orientation = props.get("orientation", "horizontal")

        props["data-slot"] = "toggle-group"
        props["data-variant"] = variant
        props["data-size"] = size
        props["data-spacing"] = spacing
        props["data-orientation"] = orientation
        props["style"] = {"gap": f"{spacing * 0.25}rem", **props.get("style", {})}

        cls.set_class_name(ClassNames.ROOT, props)
        return super().create(*children, **props)


class ToggleGroupItem(BaseUIComponent):
    tag = "Toggle"
    library = f"{PACKAGE_NAME}/toggle"

    @property
    def import_var(self):
        return ImportVar(tag="Toggle", package_path="", install=False)

    value: Var[str]
    disabled: Var[bool]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        variant = props.pop("variant", None)
        size = props.pop("size", None)

        props["data-slot"] = "toggle-group-item"
        if variant:
            props["data-variant"] = variant
        if size:
            props["data-size"] = size

        variant_classes = (
            ClassNames.ITEM_VARIANTS.get(variant)
            if variant
            else " ".join(ClassNames.ITEM_VARIANTS.values())
        )
        size_classes = (
            ClassNames.ITEM_SIZES.get(size)
            if size
            else " ".join(ClassNames.ITEM_SIZES.values())
        )

        cls.set_class_name(
            cn(
                ClassNames.ITEM_BASE,
                variant_classes,
                size_classes,
            ),
            props,
        )
        return super().create(*children, **props)


class ToggleGroup(ComponentNamespace):
    root = __call__ = staticmethod(ToggleGroupRoot.create)
    item = staticmethod(ToggleGroupItem.create)
    class_names = ClassNames


toggle_group = ToggleGroup()
