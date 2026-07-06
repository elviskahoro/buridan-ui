from reflex.components.component import Component
from reflex.vars.base import Var
from reflex_components_core.el import Div

from .core import cn


class ClassNames:
    ROOT = "animate-pulse bg-secondary"


def skeleton_component(class_name: str | Var[str] = "") -> Component:

    return Div.create(class_name=cn(ClassNames.ROOT, class_name))


skeleton = skeleton_component
