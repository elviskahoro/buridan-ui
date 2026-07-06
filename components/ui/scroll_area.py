from typing import Literal

from reflex.components.component import Component, ComponentNamespace
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var
from reflex_components_core.core.cond import cond

from .core import PACKAGE_NAME, BaseUIComponent, cn

LiteralOrientation = Literal["horizontal", "vertical"]


class ClassNames:
    ROOT = "h-full outline-none focus:outline-none"
    VIEWPORT = "h-full overscroll-contain"
    CONTENT = ""
    SCROLLBAR_BASE = "flex touch-none p-0.5 opacity-0 transition-[colors,opacity] delay-200 select-none data-hovering:opacity-100 data-hovering:delay-0 data-hovering:duration-100 data-scrolling:opacity-100 data-scrolling:delay-0 data-scrolling:duration-100"
    SCROLLBAR_VERTICAL = "w-2"
    SCROLLBAR_HORIZONTAL = "h-2"
    THUMB = "w-full rounded-full bg-secondary"
    CORNER = "bg-secondary"


class ScrollAreaBaseComponent(BaseUIComponent):
    library = f"{PACKAGE_NAME}/scroll-area"

    @property
    def import_var(self):
        return ImportVar(tag="ScrollArea", package_path="", install=False)


class ScrollAreaRoot(ScrollAreaBaseComponent):
    tag = "ScrollArea.Root"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area"
        cls.set_class_name(ClassNames.ROOT, props)
        return super().create(*children, **props)


class ScrollAreaViewport(ScrollAreaBaseComponent):
    tag = "ScrollArea.Viewport"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area-viewport"
        cls.set_class_name(ClassNames.VIEWPORT, props)
        return super().create(*children, **props)


class ScrollAreaContent(ScrollAreaBaseComponent):
    tag = "ScrollArea.Content"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area-content"
        cls.set_class_name(ClassNames.CONTENT, props)
        return super().create(*children, **props)


class ScrollAreaScrollbar(ScrollAreaBaseComponent):
    tag = "ScrollArea.Scrollbar"

    orientation: Var[LiteralOrientation] = Var.create("vertical")

    keep_mounted: Var[bool] = Var.create(False)

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area-scrollbar"
        orientation = props.get("orientation", "vertical")

        scrollbar_classes = cn(
            ClassNames.SCROLLBAR_BASE,
            cond(
                orientation == "vertical",
                ClassNames.SCROLLBAR_VERTICAL,
                ClassNames.SCROLLBAR_HORIZONTAL,
            ),
        )

        cls.set_class_name(scrollbar_classes, props)
        return super().create(*children, **props)


class ScrollAreaThumb(ScrollAreaBaseComponent):
    tag = "ScrollArea.Thumb"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area-thumb"
        cls.set_class_name(ClassNames.THUMB, props)
        return super().create(*children, **props)


class ScrollAreaCorner(ScrollAreaBaseComponent):
    tag = "ScrollArea.Corner"

    render_: Var[Component]

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        props["data-slot"] = "scroll-area-corner"
        cls.set_class_name(ClassNames.CORNER, props)
        return super().create(*children, **props)


class HighLevelScrollArea(ScrollAreaRoot):
    orientation: Var[LiteralOrientation] = Var.create("vertical")

    keep_mounted: Var[bool] = Var.create(False)

    _scrollbar_props = {"orientation", "keep_mounted"}

    @classmethod
    def create(cls, *children, **props) -> BaseUIComponent:
        scrollbar_props = {k: props.pop(k) for k in cls._scrollbar_props & props.keys()}

        return ScrollAreaRoot.create(
            ScrollAreaViewport.create(
                ScrollAreaContent.create(
                    *children,
                ),
            ),
            ScrollAreaScrollbar.create(
                ScrollAreaThumb.create(),
                **scrollbar_props,
            ),
            **props,
        )


class ScrollArea(ComponentNamespace):
    root = staticmethod(ScrollAreaRoot.create)
    viewport = staticmethod(ScrollAreaViewport.create)
    content = staticmethod(ScrollAreaContent.create)
    scrollbar = staticmethod(ScrollAreaScrollbar.create)
    thumb = staticmethod(ScrollAreaThumb.create)
    corner = staticmethod(ScrollAreaCorner.create)
    class_names = ClassNames
    __call__ = staticmethod(HighLevelScrollArea.create)


scroll_area = ScrollArea()
