import re
from collections.abc import Iterator
from typing import Any

_HEADING_RE = re.compile(r"^(#{1,2})\s+(.+)$")


def slugify(text: str) -> str:
    """Convert heading text into a DOM-id / anchor fragment.

    Mirrors the historical client-side transform (``text.toLowerCase()``
    followed by replacing every space with a dash) but runs on the server so
    the heading DOM id is a plain string rather than an unevaluated Reflex
    ``Var`` that lowers to JS. The exact transform is preserved so every
    existing in-page anchor across the docs keeps resolving.
    """
    # Despite the `str` annotation, Reflex's markdown `component_map` invokes
    # this through `render_heading` with a compile-time `Var` wrapping the
    # text, not a literal `str`; the `str()` call is load-bearing, not
    # redundant (see test_render_pre_on_mount_trigger_survives_markdown_compilation).
    return str(text).lower().replace(" ", "-")  # pyrefly: ignore[unnecessary-type-conversion]


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
        """Initialize per-slug collision counters and the TOC→DOM id queue."""
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
