import re
from collections.abc import Iterator
from typing import Any

import reflex as rx

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

_HEADING_RE = re.compile(r"^(#{1,2})\s+(.+)$")


def slugify(text: str) -> str:
    """Convert heading text into a DOM-id / anchor fragment.

    Mirrors the historical client-side transform (``text.toLowerCase()``
    followed by replacing every space with a dash) but runs on the server so
    the heading DOM id is a plain string rather than an unevaluated Reflex
    ``Var`` that lowers to JS. The exact transform is preserved so every
    existing in-page anchor across the docs keeps resolving.
    """
    return str(text).lower().replace(" ", "-")


class HeadingIdRegistry:
    """Assigns unique DOM-id slugs to the h1/h2 headings of a single doc page.

    ``render_heading`` and the TOC extractor (``app/www/generator.py``) must
    agree on exactly one id per section even when two headings normalize to the
    same slug (e.g. ``# Badge`` and ``## badge`` both slug to ``badge``). The
    registry deduplicates by suffixing later collisions (``badge``, ``badge-1``)
    so the TOC href fragment and the rendered DOM id always match exactly one
    element.

    Two-phase usage shares one set of collision counters between the TOC
    (built from a regex pass over the markdown) and the rendered DOM (built by
    ``rx.markdown``'s component map), which traverse the headings in the same
    document order:

    1. ``register(text)`` — called while iterating headings in document order
       to build ``toc_data``. Returns the deduplicated slug and queues it under
       the original heading text.
    2. ``next_id(text)`` — called by ``render_heading`` for each rendered
       heading, in the same document order. Returns and pops the queued slug,
       falling back to assigning on the fly if the heading was not
       pre-registered.
    """

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}
        self._queued: dict[str, list[str]] = {}

    def _assign(self, text: str) -> str:
        base = slugify(text)
        count = self._counts.get(base, 0)
        self._counts[base] = count + 1
        return base if count == 0 else f"{base}-{count}"

    def register(self, text: str) -> str:
        slug = self._assign(text)
        self._queued.setdefault(text, []).append(slug)
        return slug

    def next_id(self, text: str) -> str:
        queue = self._queued.get(text)
        if queue:
            return queue.pop(0)
        # Heading wasn't pre-registered (e.g. rendered without a TOC pass);
        # assign a fresh deduped id on the fly without queuing, so repeated
        # next_id calls for the same text keep suffixing instead of returning
        # the same slug from a self-populated queue.
        return self._assign(text)


# --- Helper error functions during parsing ---
def render_parse_error(msg: str) -> rx.Component:
    return rx.el.p(msg, class_name="text-sm text-red-500")


def render_heading(
    level: int,
    text: str,
    heading_id: str | None = None,
) -> rx.Component:
    normalized_id = heading_id if heading_id is not None else slugify(text)

    if level == 1:
        return rx.el.h1(
            rx.el.a(
                rx.el.span(
                    text,
                    class_name="hover:underline hover:underline-offset-6",
                ),
                href=f"#{normalized_id}",
                class_name=(
                    "after:content-['#'] after:ml-2 after:opacity-0 hover:after:opacity-100 after:text-muted-foreground"
                ),
            ),
            class_name=HEADING_1_CLASS if level == 1 else HEADING_2_CLASS,
            id=normalized_id,
        )

    return rx.el.h2(
        rx.el.a(
            rx.el.span(
                text,
                class_name="hover:underline hover:underline-offset-6",
            ),
            href=f"#{normalized_id}",
            class_name=(
                "after:content-['#'] after:ml-2 after:opacity-0 hover:after:opacity-100 after:text-muted-foreground"
            ),
        ),
        class_name=HEADING_1_CLASS if level == 1 else HEADING_2_CLASS,
        id=normalized_id,
    )


def render_paragraph(text: str) -> rx.Component:
    return rx.el.p(text, class_name=PARAGRAPH_CLASS)


def render_list_item(text: str) -> rx.Component:
    return rx.list_item(rx.el.p(text, class_name=LIST_ITEM_CLASS))


def render_link(*args: Any, **props: Any) -> rx.Component:
    # Reflex builds Markdown map callbacks without the runtime href; ReactMarkdown
    # supplies it through the props spread, which keeps this a native Radix link.
    return rx.link(*args, class_name=LINK_CLASS, **props)


def render_pre(*children: Any, **props: Any) -> rx.Component:
    language = props.get("language")

    return rx.el.div(
        rx.el.div(
            rx.cond(
                language != "python",
                rx.el.div(
                    rx.el.p(
                        language,
                        class_name="text-muted-foreground text-sm font-normal px-[1rem] py-2",
                    ),
                    class_name="w-full border-b border-input/70 flex flex-row items-center justify-between",
                ),
            ),
            rx.el.div(
                rx.el.pre(
                    rx.el.code(
                        *children,
                        style={
                            "white-space": "pre",
                            "color": "var(--foreground)",
                            "font-size": "13px !important",
                            "padding": "1rem 1rem",
                            "display": "block",
                        },
                        class_name="language-python",
                    ),
                ),
                class_name="overflow-x-auto overflow-y-auto scrollbar-none flex-1 min-h-0 pr-[1rem]",
            ),
            class_name="w-full flex-1 min-h-0 flex flex-col h-full",
        ),
        class_name="rounded-[1rem] flex-1 min-h-0 flex flex-col bg-secondary dark:bg-card my-4",
    )


def render_blockquote(*children: Any, **props: Any) -> rx.Component:
    return rx.el.div(
        *children,
        class_name="w-full rounded-[1rem] bg-secondary dark:bg-card flex items-center justify-center p-4 mb-4 "
        "[&>p]:mb-0 [&>p]:leading-6",
    )


# --- Final Component Map ---
markdown_component_map = {
    "h1": lambda text: render_heading(1, text),
    "h2": lambda text: render_heading(2, text),
    "p": render_paragraph,
    "li": render_list_item,
    "a": render_link,
    "blockquote": render_blockquote,
    "code": lambda text: rx.el.span(text, class_name="bg-secondary rounded-md p-1"),
    "pre": render_pre,
    "table": lambda *children, **props: rx.el.div(
        rx.el.div(
            rx.el.table(
                *children,
                **props,
                class_name="w-max min-w-full",
            ),
            class_name="w-full overflow-x-auto scrollbar-none",
        ),
        class_name="w-full !text-sm rounded-[1rem] border border-input mb-4",
    ),
    "thead": lambda *children, **props: rx.el.thead(
        *children,
        **props,
        class_name="border-input border-b",
    ),
    "tbody": lambda *children, **props: rx.el.tbody(
        *children,
        **props,
        class_name="divide-input divide-y",
    ),
    "tr": lambda *children, **props: rx.el.tr(
        *children,
        **props,
        class_name="m-0 p-0",
    ),
    "th": lambda *children, **props: rx.el.th(
        *children,
        **props,
        class_name=(
            "px-4 py-2 text-left font-bold "
            "[&[align=center]]:text-center "
            "whitespace-nowrap "
            "[&[align=right]]:text-right"
        ),
    ),
    "td": lambda *children, **props: rx.el.td(
        *children,
        **props,
        class_name=(
            "px-4 py-2 text-left "
            "[&[align=center]]:text-center "
            "whitespace-nowrap "
            "[&[align=right]]:text-right"
        ),
    ),
}


def iter_heading_segments(text: str) -> Iterator[tuple[str, Any]]:
    """Yield ``('heading', (level, text))`` and ``('text', body)`` segments.

    Splits a markdown chunk at every h1/h2 (``#`` / ``##``) line so the parser
    can render headings server-side with pre-computed DOM ids (see
    :class:`HeadingIdRegistry`) and feed only the prose between them to
    ``rx.markdown``.

    Code-fence aware: ``#``-lines inside a fenced code block (``` or ~~~) are
    treated as code, not headings — so a ``#``-comment in a fenced code block
    never becomes a phantom section. This matches how ``rx.markdown`` (via
    remark) parses the surrounding prose, keeping the TOC extractor and the
    rendered DOM in lock-step on exactly the same set of headings.
    """
    lines = text.split("\n")
    in_fence = False
    fence_marker = ""
    buf: list[str] = []

    def flush() -> Iterator[tuple[str, str]]:
        if buf:
            yield ("text", "\n".join(buf))
            buf.clear()

    for line in lines:
        stripped = line.lstrip()
        starts_fence = stripped.startswith(("```", "~~~"))

        if not in_fence and starts_fence:
            in_fence = True
            fence_marker = stripped[:3]
            buf.append(line)
            continue

        if in_fence and stripped.startswith(fence_marker):
            in_fence = False
            fence_marker = ""
            buf.append(line)
            continue

        if in_fence:
            buf.append(line)
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            yield from flush()
            level = len(heading_match.group(1))
            yield ("heading", (level, heading_match.group(2).strip()))
            continue

        buf.append(line)

    yield from flush()
