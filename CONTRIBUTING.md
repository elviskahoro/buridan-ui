# Contributing to Buridan UI

We love contributions! Whether you're fixing a bug, adding a new component, or improving the theme engine, here's how you can help.

## Development Setup

1. Fork and clone the repository.
2. Install dependencies using `uv` (recommended) or `pip install -r requirements.txt`.
3. Run the development server: `reflex run`.

## Frontend dependency security fixes

Reflex 0.10.0 restores `reflex.lock/package.json` and `reflex.lock/bun.lock`
when generating `.web`. Keep both files committed together. Put transitive
security pins in the persisted manifest's `overrides`, then let Bun generate
the matching lockfile:

```sh
cd reflex.lock
bun install --lockfile-only
bun audit
```

Use Bun 1.4 or newer, which supports this lockfile format. To verify a fresh
frontend generation and production build, run from the repository root:

```sh
REFLEX_WEB_WORKDIR=.web-security-check uv run reflex export --frontend-only --no-zip
cd .web-security-check
bun install --frozen-lockfile
bun audit
```

Remove `.web-security-check` after verification. Preserve the security overrides
when updating dependencies: the current pins patch KaTeX, postcss-selector-parser,
socket.io-parser, source-map-js, and ws. KaTeX, postcss-selector-parser, and ws
exceed their parents' declared version ranges; check Markdown math rendering,
Tailwind typography output, and WebSocket connections when changing those
overrides. Reassess the pins when their parent packages support patched versions
directly.

### Known advisories pinned by Reflex 0.10.0

The following advisories are pinned by upstream Reflex 0.10.0 dependencies and
cannot be upgraded without a Reflex version bump:

- **vite 8.3.2**: Multiple moderate to high severity advisories (cross-origin script
  execution, file serving restrictions, editor flag misinterpretation). Reflex 0.10.0
  pins vite via @react-router/dev.
- **KaTeX, postcss-selector-parser**: Patched via security overrides in the
  manifest's `overrides` section.

## Adding Components

- New components should be added to `app/base_ui/components/base/`.
- Use `CoreComponent` or `BaseUIComponent` as base classes to ensure theme compatibility.
- Use `oklch` CSS variables for all colors.

## Adding Examples

- Add your example card to `app/examples/components.py`.
- Use the `@masonry_card(label="Category")` decorator.
- Categories include: `General`, `Finance`, `Healthcare`, `Tech`, `Government`.

## Coding Standards

- Follow PEP 8 for Python code.
- Ensure all components are accessible (ARIA roles, keyboard support).
- Use `rx.cond` and `rx.match` for dynamic, client-side logic where possible.

## Pull Requests

- Create a feature branch for your changes.
- Provide a clear description of the problem solved or the feature added.
- Include a screenshot or recording of new UI components.

Thank you for helping make Buridan UI the standard for Reflex applications!
