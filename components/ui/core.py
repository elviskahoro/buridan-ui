from typing import Any, ClassVar

import reflex as rx
from reflex.components.component import Component
from reflex.utils.imports import ImportVar
from reflex.vars import FunctionVar, Var
from reflex.vars.base import VarData

PACKAGE_NAME = "@base-ui/react"
PACKAGE_VERSION = "1.6.0"
PACKAGE_CLSX = "clsx@2.1.1"
PACKAGE_TAILWIND_MERGE = "tailwind-merge@3.7.0"
CLSX = Var(
    "clsx",
    _var_data=VarData(
        imports={PACKAGE_CLSX: ImportVar(tag="clsx", package_path="")}
    ),
).to(FunctionVar)
TW_MERGE = Var(
    "twMerge",
    _var_data=VarData(
        imports={
            PACKAGE_TAILWIND_MERGE: ImportVar(tag="twMerge", package_path="")
        }
    ),
).to(FunctionVar)


class CoreComponent(Component):
    unstyled: Var[bool]
    _merge_default_classes_with_render: ClassVar[bool] = False

    @classmethod
    def set_class_name(
        cls, default_class_name: str | Var[str], props: dict[str, Any]
    ) -> None:
        if "render_" in props and not cls._merge_default_classes_with_render:
            return

        props_class_name = props.get("class_name", "")
        unstyled = props.pop("unstyled", None)

        if unstyled is True:
            props["class_name"] = props_class_name
            return

        merged = cn(default_class_name, props_class_name)
        if isinstance(unstyled, Var):
            props["class_name"] = rx.cond(unstyled, props_class_name, merged)
            return

        props["class_name"] = merged

    def _exclude_props(self) -> list[str]:
        return [
            *super()._exclude_props(),
            "unstyled",
        ]


class BaseUIComponent(CoreComponent):
    lib_dependencies: list[str] = [f"{PACKAGE_NAME}@{PACKAGE_VERSION}"]


def cn(*classes: Var | str | tuple | list | None) -> Var:
    return TW_MERGE.call(CLSX.call(*classes)).to(str)
