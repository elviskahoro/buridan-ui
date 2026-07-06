from reflex.components.component import ComponentNamespace
from reflex_components_core.el import Div
from reflex_components_core.el import Kbd as ElKbd

from .core import CoreComponent, cn


class ClassNames:
    KBD = (
        "pointer-events-none inline-flex h-5 w-fit min-w-5 items-center justify-center gap-1 "
        "rounded-sm bg-muted px-1 font-sans text-xs font-medium text-muted-foreground select-none "
        "in-data-[slot=tooltip-popup]:bg-background/20 in-data-[slot=tooltip-popup]:text-background "
        "dark:in-data-[slot=tooltip-popup]:bg-background/10 [&_svg:not([class*='size-'])]:size-3"
    )

    GROUP = "inline-flex items-center gap-1"


class KbdRoot(ElKbd, CoreComponent):
    @classmethod
    def create(cls, *children, **props) -> ElKbd:
        custom_classes = props.pop("class_name", "")
        props["data-slot"] = "kbd"

        cls.set_class_name(cn(ClassNames.KBD, custom_classes), props)
        return super().create(*children, **props)


class KbdGroupContainer(Div, CoreComponent):
    @classmethod
    def create(cls, *children, **props) -> Div:
        custom_classes = props.pop("class_name", "")
        props["data-slot"] = "kbd-group"

        cls.set_class_name(cn(ClassNames.GROUP, custom_classes), props)
        return super().create(*children, **props)


class KbdNamespace(ComponentNamespace):
    root = staticmethod(KbdRoot.create)
    group = staticmethod(KbdGroupContainer.create)
    class_names = ClassNames


kbd = KbdNamespace()
