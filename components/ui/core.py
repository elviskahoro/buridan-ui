from typing import Any

from reflex.components.component import Component
from reflex.utils.imports import ImportVar
from reflex.vars import FunctionVar, Var
from reflex.vars.base import VarData

PACKAGE_NAME = "@base-ui/react"
PACKAGE_VERSION = "1.6.0"
PACKAGE_CLSX = "clsx@2.1.1"
PACKAGE_TAILWIND_MERGE = "tailwind-merge@3.7.0"
CLSX = Var(
    "clsx", _var_data=VarData(imports={PACKAGE_CLSX: ImportVar(tag="clsx")})
).to(FunctionVar)
TW_MERGE = Var(
    "twMerge",
    _var_data=VarData(
        imports={PACKAGE_TAILWIND_MERGE: ImportVar(tag="twMerge")}
    ),
).to(FunctionVar)


class CoreComponent(Component):
    unstyled: Var[bool]

    @classmethod
    def set_class_name(
        cls, default_class_name: str | Var[str], props: dict[str, Any]
    ) -> None:

        if "render_" in props:
            return

        props_class_name = props.get("class_name", "")

        if props.pop("unstyled", False):
            props["class_name"] = props_class_name
            return

        props["class_name"] = cn(default_class_name, props_class_name)

    def _exclude_props(self) -> list[str]:
        return [
            *super()._exclude_props(),
            "unstyled",
        ]


class BaseUIComponent(CoreComponent):
    lib_dependencies: list[str] = [f"{PACKAGE_NAME}@{PACKAGE_VERSION}"]


def cn(*classes: Var | str | tuple | list | None) -> Var:
    return TW_MERGE.call(CLSX.call(*classes)).to(str)
