import reflex as rx
from reflex.components.component import Component, ComponentNamespace
from reflex.event import EventHandler, passthrough_event_spec
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var

from .core import PACKAGE_NAME, BaseUIComponent, cn


class ClassNames:
    ROOT = "flex flex-col justify-center text-secondary-12"
    TRIGGER = "group flex items-center gap-2"
    PANEL = "flex h-[var(--collapsible-panel-height)] flex-col justify-end overflow-hidden text-sm transition-[height] duration-200 ease-out data-[ending-style]:h-0 data-[starting-style]:h-0"
    PANEL_DIV = ""


class CollapsibleBaseComponent(BaseUIComponent):
    library = f"{PACKAGE_NAME}/collapsible"

    @property
    def import_var(self):
        return ImportVar(tag="Collapsible", package_path="", install=False)


class CollapsibleRoot(CollapsibleBaseComponent):
    tag = "Collapsible.Root"

    default_open: Var[bool]
    open: Var[bool]
    on_open_change: EventHandler[passthrough_event_spec(bool)]
    disabled: Var[bool]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "collapsible"
        cls.set_class_name(ClassNames.ROOT, props)
        return super().create(*children, **props)


class CollapsibleTrigger(CollapsibleBaseComponent):
    tag = "Collapsible.Trigger"

    native_button: Var[bool]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "collapsible-trigger"
        cls.set_class_name(ClassNames.TRIGGER, props)
        return super().create(*children, **props)


class CollapsiblePanel(CollapsibleBaseComponent):
    tag = "Collapsible.Panel"

    hidden_until_found: Var[bool]
    keep_mounted: Var[bool]
    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "collapsible-panel"
        inner_class = props.pop("class_name", "")
        cls.set_class_name(ClassNames.PANEL, props)
        return super().create(
            rx.el.div(*children, class_name=cn(ClassNames.PANEL_DIV, inner_class)),
            **props,
        )


class Collapsible(ComponentNamespace):
    root = staticmethod(CollapsibleRoot.create)
    trigger = staticmethod(CollapsibleTrigger.create)
    panel = staticmethod(CollapsiblePanel.create)
    class_names = ClassNames


collapsible = Collapsible()
