from collections.abc import Callable
from typing import Any

import reflex as rx

from app.www.style import slugify

# Reflex's component factories (rx.el.*, rx.cond, ...) are untyped, so pyright
# reports reportUnknownMemberType on every call. Route calls through an Any alias;
# keep `rx` for real annotations like rx.Component.
_rx: Any = rx

PARAGRAPH_CLASS = "text-sm leading-7 mb-4"

HEADING_1_CLASS = "text-2xl font-semibold mt-8 mb-3 first:mt-0 scroll-mt-14"

HEADING_2_CLASS = "text-xl font-semibold mt-6 mb-2 scroll-mt-14"

LIST_ITEM_CLASS = "text-sm leading-7 text-slate-11"

LINK_CLASS = (
    "font-medium "
    "text-foreground "
    "underline underline-offset-4 "
    "decoration-foreground "
    "hover:!text-foreground "
    "hover:!decoration-foreground"
)


# --- Helper error functions during parsing ---
def render_parse_error(msg: str) -> rx.Component:
    return _rx.el.p(msg, class_name="text-sm text-red-500")


def render_heading(
    level: int,
    text: str,
    heading_id: str | None = None,
) -> rx.Component:
    normalized_id = heading_id if heading_id is not None else slugify(text)

    if level == 1:
        return _rx.el.h1(
            _rx.el.a(
                _rx.el.span(
                    text,
                    class_name="hover:underline hover:underline-offset-6",
                ),
                href=f"#{normalized_id}",
                class_name=(
                    "after:content-['#'] after:ml-2 after:opacity-0 hover:after:opacity-100 after:text-muted-foreground"
                ),
            ),
            class_name=HEADING_1_CLASS,
            id=normalized_id,
        )

    return _rx.el.h2(
        _rx.el.a(
            _rx.el.span(
                text,
                class_name="hover:underline hover:underline-offset-6",
            ),
            href=f"#{normalized_id}",
            class_name=(
                "after:content-['#'] after:ml-2 after:opacity-0 hover:after:opacity-100 after:text-muted-foreground"
            ),
        ),
        class_name=HEADING_2_CLASS,
        id=normalized_id,
    )


def render_paragraph(text: str) -> rx.Component:
    return _rx.el.p(text, class_name=PARAGRAPH_CLASS)


def render_list_item(text: str) -> rx.Component:
    return _rx.list_item(_rx.el.p(text, class_name=LIST_ITEM_CLASS))


def render_heading_1(text: str) -> rx.Component:
    return render_heading(1, text)


def render_heading_2(text: str) -> rx.Component:
    return render_heading(2, text)


def render_code(text: str) -> rx.Component:
    return _rx.el.span(text, class_name="bg-secondary rounded-md p-1")


def render_table(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.div(
        _rx.el.div(
            _rx.el.table(
                *children,
                **props,
                class_name="w-max min-w-full",
            ),
            class_name="w-full overflow-x-auto scrollbar-none",
        ),
        class_name="w-full !text-sm rounded-[1rem] border border-input mb-4",
    )


def render_thead(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.thead(
        *children,
        **props,
        class_name="border-input border-b",
    )


def render_tbody(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.tbody(
        *children,
        **props,
        class_name="divide-input divide-y",
    )


def render_tr(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.tr(
        *children,
        **props,
        class_name="m-0 p-0",
    )


def render_th(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.th(
        *children,
        **props,
        class_name=(
            "px-4 py-2 text-left font-bold "
            "[&[align=center]]:text-center "
            "whitespace-nowrap "
            "[&[align=right]]:text-right"
        ),
    )


def render_td(*children: Any, **props: Any) -> rx.Component:
    return _rx.el.td(
        *children,
        **props,
        class_name=(
            "px-4 py-2 text-left "
            "[&[align=center]]:text-center "
            "whitespace-nowrap "
            "[&[align=right]]:text-right"
        ),
    )


def render_link(*args: Any, **props: Any) -> rx.Component:
    # Reflex builds Markdown map callbacks without the runtime href; ReactMarkdown
    # supplies it through the props spread, which keeps this a native Radix link.
    return _rx.link(*args, class_name=LINK_CLASS, **props)


def render_pre(*children: Any, **props: Any) -> rx.Component:
    language = props.get("language")

    code_class = _rx.cond(
        language == "bash",
        "language-bash",
        _rx.cond(
            language == "uv",
            "language-bash",
            _rx.cond(
                language == "css",
                "language-css",
                _rx.cond(
                    language == "assets/globals.css",
                    "language-css",
                    _rx.cond(
                        language == "toml",
                        "language-toml",
                        _rx.cond(
                            language == "pyproject.toml",
                            "language-toml",
                            _rx.cond(
                                language == "text",
                                "language-text",
                                "language-python",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    return _rx.el.div(
        _rx.el.div(
            _rx.cond(
                language != "python",
                _rx.el.div(
                    _rx.el.p(
                        language,
                        class_name="text-muted-foreground text-sm font-normal px-[1rem] py-2",
                    ),
                    class_name="w-full border-b border-input/70 flex flex-row items-center justify-between",
                ),
            ),
            _rx.el.div(
                _rx.el.pre(
                    _rx.el.code(
                        *children,
                        style={
                            "white-space": "pre",
                            "color": "var(--foreground)",
                            "font-size": "13px !important",
                            "padding": "1rem 1rem",
                            "display": "block",
                        },
                        class_name=code_class,
                        on_mount=_rx.call_script("Prism.highlightAll()"),
                    ),
                ),
                class_name="overflow-x-auto overflow-y-auto scrollbar-none flex-1 min-h-0 pr-[1rem]",
            ),
            class_name="w-full flex-1 min-h-0 flex flex-col h-full",
        ),
        class_name="rounded-[1rem] flex-1 min-h-0 flex flex-col bg-secondary dark:bg-card my-4",
    )


def render_blockquote(*children: Any) -> rx.Component:
    return _rx.el.div(
        *children,
        class_name="w-full rounded-[1rem] bg-secondary dark:bg-card flex items-center justify-center p-4 mb-4 "
        "[&>p]:mb-0 [&>p]:leading-6",
    )


# --- Final Component Map ---
markdown_component_map: dict[str, Callable[..., rx.Component]] = {
    "h1": render_heading_1,
    "h2": render_heading_2,
    "p": render_paragraph,
    "li": render_list_item,
    "a": render_link,
    "blockquote": render_blockquote,
    "code": render_code,
    "pre": render_pre,
    "table": render_table,
    "thead": render_thead,
    "tbody": render_tbody,
    "tr": render_tr,
    "th": render_th,
    "td": render_td,
}
