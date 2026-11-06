from typing import Any, Literal, Self

from reflex.components.component import ComponentNamespace
from reflex.vars.base import Var
from reflex_components_core.core.foreach import foreach  # pyright: ignore[reportUnknownVariableType]  # imported foreach stub is untyped
from reflex_components_core.el import (
    Caption,
    Div,
    Table,
    Tbody,
    Td,
    Tfoot,
    Th,
    Thead,
    Tr,
)

from .core import CoreComponent, cn

LiteralAlign = Literal["left", "center", "right"]


class ClassNames:
    ROOT = "w-full overflow-auto rounded-lg border border-input bg-card shadow-sm"
    TABLE = "w-full caption-bottom text-sm border-collapse"
    HEADER = "[&_tr]:border-b bg-secondary/50 backdrop-blur-sm sticky top-0"
    BODY = "[&_tr:last-child]:border-0"
    FOOTER = "border-t bg-muted/50 font-medium [&>tr]:last:border-b-0"
    ROW = "border-b transition-colors data-[state=selected]:bg-muted hover:bg-muted/50"
    HEAD = "h-10 px-4 text-left align-middle font-semibold text-muted-foreground [&:has([role=checkbox])]:pr-0 whitespace-nowrap"
    CELL = "p-4 align-middle [&:has([role=checkbox])]:pr-0"
    CAPTION = "mt-4 text-sm text-muted-foreground"


class TableRoot(CoreComponent, Div):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:

        cls.set_class_name(ClassNames.ROOT, props)

        table_props: dict[str, Any] = {
            "class_name": ClassNames.TABLE,
        }
        return super().create(Table.create(*children, **table_props), **props)


class TableHeader(CoreComponent, Thead):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.HEADER, props)
        return super().create(*children, **props)


class TableBody(CoreComponent, Tbody):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.BODY, props)
        return super().create(*children, **props)


class TableFooter(CoreComponent, Tfoot):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.FOOTER, props)
        return super().create(*children, **props)


class TableRow(CoreComponent, Tr):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.ROW, props)
        return super().create(*children, **props)


class TableHead(CoreComponent, Th):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.HEAD, props)
        return super().create(*children, **props)


class TableCell(CoreComponent, Td):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.CELL, props)
        return super().create(*children, **props)


class TableCaption(CoreComponent, Caption):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.CAPTION, props)
        return super().create(*children, **props)


def high_level_table(
    data: Var[list[dict[str, Any]]] | list[dict[str, Any]],
    columns: list[dict[str, Any]] | None = None,
    *,
    striped: bool = False,
    **props: Any,
) -> TableRoot:
    if columns is None and isinstance(data, list) and len(data) > 0:
        columns = [
            {"header": k.replace("_", " ").title(), "accessor": k} for k in data[0]
        ]
    elif columns is None:
        columns = []

    header_row = TableRow.create(
        *[
            TableHead.create(
                col.get("header", ""),
                class_name=cn(
                    "text-right" if col.get("align") == "right" else "",
                    "text-center" if col.get("align") == "center" else "",
                    col.get("class_name", ""),
                ),
            )
            for col in columns
        ],
    )

    if isinstance(data, Var):

        def render_row(row: dict[str, Any]) -> TableRow:
            return TableRow.create(
                *[
                    TableCell.create(
                        row[col["accessor"]],
                        class_name=cn(
                            "text-right" if col.get("align") == "right" else "",
                            "text-center" if col.get("align") == "center" else "",
                            col.get("class_name", ""),
                        ),
                    )
                    for col in columns
                ],
                class_name=cn(
                    "even:bg-secondary/30" if striped else "",
                ),
            )

        body_content = foreach(data, render_row)
    else:
        body_content = [
            TableRow.create(
                *[
                    TableCell.create(
                        row.get(col["accessor"], ""),
                        class_name=cn(
                            "text-right" if col.get("align") == "right" else "",
                            "text-center" if col.get("align") == "center" else "",
                            col.get("class_name", ""),
                        ),
                    )
                    for col in columns
                ],
                class_name=cn(
                    "even:bg-secondary/30" if striped and i % 2 == 1 else "",
                ),
            )
            for i, row in enumerate(data)
        ]

    return TableRoot.create(
        TableHeader.create(header_row),
        TableBody.create(
            body_content,
        ),
        **props,
    )


class TableNamespace(ComponentNamespace):
    root = staticmethod(TableRoot.create)
    header = staticmethod(TableHeader.create)
    body = staticmethod(TableBody.create)
    footer = staticmethod(TableFooter.create)
    row = staticmethod(TableRow.create)
    head = staticmethod(TableHead.create)
    cell = staticmethod(TableCell.create)
    caption = staticmethod(TableCaption.create)
    __call__ = staticmethod(high_level_table)


table = TableNamespace()


class HighLevelTable(TableRoot):
    """Deprecated: use `high_level_table` or the `table(...)` namespace call.

    Kept as a `TableRoot` subclass so `isinstance`/`issubclass` checks on
    out-of-tree code still hold; `.create(...)` delegates to the new
    module-level factory.
    """

    @classmethod
    def create(  # pyrefly: ignore[bad-override]
        cls,
        *args: Any,
        **kwargs: Any,
    ) -> TableRoot:
        return high_level_table(*args, **kwargs)
