from typing import Any, Literal, Self, cast

import reflex as rx
from reflex.components.component import ComponentNamespace
from reflex.vars.base import Var
from reflex_components_core.el import Div

from .core import CoreComponent, cn

LiteralTrendDirection = Literal["up", "down", "neutral"]


class ClassNames:
    ROOT = "flex flex-col gap-y-2 p-4 rounded-lg border border-input bg-card shadow-sm"
    LABEL = "text-sm font-medium text-muted-foreground"
    VALUE = "text-3xl font-bold tracking-tight text-foreground"
    TREND_CONTAINER = "flex flex-row items-center gap-x-1.5"
    TREND_BADGE = "flex flex-row items-center gap-x-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider"


class MetricRoot(CoreComponent, Div):
    @classmethod
    def create(cls, *children: Any, **props: Any) -> Self:
        cls.set_class_name(ClassNames.ROOT, props)
        return super().create(*children, **props)


def high_level_metric(
    label: Var[str] | str,
    value: Var[str] | str,
    trend: Var[str] | str | None = None,
    trend_direction: Var[LiteralTrendDirection] | LiteralTrendDirection = "neutral",
    **props: Any,
) -> MetricRoot:
    trend_color = rx.match(  # pyright: ignore[reportUnknownVariableType]  # rx.match overload yields Var[Unknown]
        trend_direction,
        ("up", "text-emerald-600 bg-emerald-500/10 dark:text-emerald-400"),
        ("down", "text-destructive bg-destructive/10"),
        "text-muted-foreground bg-secondary",
    )

    return MetricRoot.create(
        rx.el.div(
            rx.el.p(label, class_name=ClassNames.LABEL),
            class_name="flex flex-row items-center justify-between w-full",
        ),
        rx.el.div(
            rx.el.p(value, class_name=ClassNames.VALUE),
            rx.cond(
                trend,
                rx.el.div(
                    rx.el.div(
                        rx.el.span(trend),
                        class_name=cn(
                            ClassNames.TREND_BADGE,
                            cast("Var[Any]", trend_color),
                        ),
                    ),
                    class_name=ClassNames.TREND_CONTAINER,
                ),
            ),
            class_name="flex flex-row items-baseline justify-between w-full",
        ),
        **props,
    )


class MetricNamespace(ComponentNamespace):
    root = staticmethod(MetricRoot.create)
    __call__ = staticmethod(high_level_metric)


metric = MetricNamespace()


class HighLevelMetric(MetricRoot):
    """Deprecated: use `high_level_metric` or the `metric(...)` namespace call.

    Kept as a `MetricRoot` subclass so `isinstance`/`issubclass` checks on
    out-of-tree code still hold; `.create(...)` delegates to the new
    module-level factory.
    """

    @classmethod
    def create(  # pyrefly: ignore[bad-override]
        cls,
        *args: Any,
        **kwargs: Any,
    ) -> MetricRoot:
        return high_level_metric(*args, **kwargs)
