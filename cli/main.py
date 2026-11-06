import argparse
import ast
import shutil
import sys
from pathlib import Path
from typing import Any, TypeGuard

# ── registries ────────────────────────────────────────────────────────────────
from app.registry.colors import COLOR_THEMES
from app.registry.components import COMPONENT_REGISTRY
from app.registry.fonts import FONT_REGISTRY
from app.registry.radii import RADIUS_OPTIONS
from app.registry.styles import STYLE_REGISTRY
from app.registry.themes import BASE_THEMES
from cli.scrollbar_css import SCROLLBAR_CSS
from cli.shimmer_css import SHIMMER_CSS

# ── string constants ──────────────────────────────────────────────────────────
from cli.tailwind_config import TAILWIND_CONFIG_SNIPPET

# ── utilities bundle injected by `buridan init` ───────────────────────────────
# Order matters — each block is appended in sequence.
UTILITIES_BUNDLE = [
    ("shimmer", SHIMMER_CSS),
    ("scrollbar", SCROLLBAR_CSS),
]

# Sentinel comments used to detect whether a utility is already present.
UTILITY_SENTINELS = {
    "shimmer": "/* ── Shimmer utility",
    "scrollbar": "/* ── Scrollbar utilities",
}

# Derived radius scale emitted alongside the `:root` / `.dark` blocks so that
# the CLI-injected Tailwind `borderRadius` mapping (`var(--radius-sm)` …
# `var(--radius-4xl)`) resolves in generated projects. Mirrors the
# `@theme inline` block in this repo's own `assets/globals.css`.
RADIUS_SCALE_BLOCK = """@theme inline {
    --radius-sm: calc(var(--radius) * 0.6);
    --radius-md: calc(var(--radius) * 0.8);
    --radius-lg: var(--radius);
    --radius-xl: calc(var(--radius) * 1.4);
    --radius-2xl: calc(var(--radius) * 1.8);
    --radius-3xl: calc(var(--radius) * 2.2);
    --radius-4xl: calc(var(--radius) * 2.6);
}"""


# ── helpers ───────────────────────────────────────────────────────────────────

SEED_LENGTH = 9
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
COLOR_RADIX = len(COLOR_THEMES) + 1
SEED_SPACE_SIZE = (
    len(BASE_THEMES)
    * COLOR_RADIX**2
    * len(STYLE_REGISTRY)
    * len(FONT_REGISTRY)
    * len(RADIUS_OPTIONS)
)


def from_base62(s: str) -> int:
    n = 0
    for i in range(len(s) - 1, -1, -1):
        n = n * 62 + CHARS.find(s[i])
    return n


def flatten_vars(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in obj.items():
        key = "--radius" if k == "radius" else f"--{k}"
        out[key] = v
    return out


def _lookup(
    seq: list[dict[str, Any]],
    entry_id: str | None,
) -> dict[str, Any] | None:
    if not entry_id:
        return None
    return next((x for x in seq if x["id"] == entry_id), None)


def _apply_color_overlays(
    theme: dict[str, Any],
    entry: dict[str, Any] | None,
    *,
    dark: bool,
    chart: bool,
) -> None:
    """Overlay the chart vars (chart=True) or the non-chart vars from `entry`."""
    if not entry:
        return
    for k, v in flatten_vars(entry["dark"] if dark else entry["light"]).items():
        if k.startswith("--chart-") == chart:
            theme[k] = v


def rebuild_theme(config: dict[str, Any]) -> dict[str, Any]:
    base_id = config.get("baseId")
    color_id = config.get("colorId")
    chart_id = config.get("chartId")
    style_id = config.get("styleId")
    font_id = config.get("fontId")
    radius = config.get("radius")
    dark = config.get("darkMode", False)

    base = _lookup(BASE_THEMES, base_id)
    if not base:
        return {}

    theme = {**flatten_vars(base["dark"] if dark else base["light"])}

    _apply_color_overlays(
        theme,
        _lookup(COLOR_THEMES, color_id),
        dark=dark,
        chart=False,
    )
    _apply_color_overlays(theme, _lookup(COLOR_THEMES, chart_id), dark=dark, chart=True)

    for registry, entry_id in ((STYLE_REGISTRY, style_id), (FONT_REGISTRY, font_id)):
        entry = _lookup(registry, entry_id)
        if entry:
            theme.update(entry["vars"])

    if radius:
        theme["--radius"] = radius

    return theme


def decode_seed(seed: str) -> dict[str, Any] | None:
    if not seed:
        return None
    if seed == "b0":
        return {
            "baseId": BASE_THEMES[0]["id"],
            "colorId": None,
            "chartId": None,
            "styleId": STYLE_REGISTRY[0]["id"],
            "fontId": FONT_REGISTRY[0]["id"],
            "radius": RADIUS_OPTIONS[2][1],
        }
    if len(seed) != SEED_LENGTH:
        return None

    n = from_base62(seed[:4])
    checksum = from_base62(seed[4:])

    if checksum == (n * 12345) % 916132832 and n < SEED_SPACE_SIZE:
        temp = n
        r_idx = temp % len(RADIUS_OPTIONS)
        temp //= len(RADIUS_OPTIONS)
        f_idx = temp % len(FONT_REGISTRY)
        temp //= len(FONT_REGISTRY)
        s_idx = temp % len(STYLE_REGISTRY)
        temp //= len(STYLE_REGISTRY)
        ch_idx = temp % COLOR_RADIX
        temp //= COLOR_RADIX
        c_idx = temp % COLOR_RADIX
        temp //= COLOR_RADIX
        b_idx = temp % len(BASE_THEMES)

        return {
            "baseId": BASE_THEMES[b_idx]["id"],
            "colorId": COLOR_THEMES[c_idx - 1]["id"] if c_idx > 0 else None,
            "chartId": COLOR_THEMES[ch_idx - 1]["id"] if ch_idx > 0 else None,
            "styleId": STYLE_REGISTRY[s_idx]["id"],
            "fontId": FONT_REGISTRY[f_idx]["id"],
            "radius": RADIUS_OPTIONS[r_idx][1],
        }
    return None


def format_css(config: dict[str, Any]) -> str:
    return "\n".join(f"    {k}: {v};" for k, v in config.items() if k.startswith("--"))


def generate_theme_css(seed: str) -> str:
    def build(*, dark: bool) -> str:
        return format_css(
            rebuild_theme({**(decode_seed(seed) or {}), "darkMode": dark}),
        )

    return (
        f":root {{\n{build(dark=False)}\n}}\n\n"
        f".dark {{\n{build(dark=True)}\n}}\n\n"
        f"{RADIUS_SCALE_BLOCK}"
    )


def get_source_root() -> Path | None:
    source_root = Path(__file__).parent.parent
    if (source_root / "components").exists():
        return source_root
    try:
        import components

        return Path(components.__file__).parent.parent
    except (ImportError, AttributeError):
        return None


def resolve_dependencies(
    component_names: list[str],
    registry: dict[str, Any],
) -> list[str]:
    required_files: set[str] = set()
    visited: set[str] = set()

    def add(name: str) -> None:
        key = name.lower()
        if key in visited:
            return
        visited.add(key)
        entry = registry.get(key)
        if not entry:
            print(f"Warning: Component '{name}' not found in registry.")
            return
        for f in entry["files"]:
            required_files.add(f)
        for dep in entry.get("dependencies", []):
            add(dep)

    for name in component_names:
        add(name)

    return sorted(required_files)


BLOCK_SOURCE_PREFIX = "app/www/library/blocks/"


def remap_dest(rel: str) -> str:
    """Remap block source paths to blocks/ in the user's project root."""
    if rel.startswith(BLOCK_SOURCE_PREFIX):
        return "blocks/" + Path(rel).name
    return rel


def add_components_to_project(
    component_names: list[str],
    target_root: Path | None = None,
) -> bool:
    if target_root is None:
        target_root = Path.cwd()

    if not (target_root / "rxconfig.py").exists():
        print(
            "Error: rxconfig.py not found. Please run this command in a Reflex project root.",
        )
        return False

    source_root = get_source_root()
    if not source_root:
        print("Error: Could not locate Buridan source components.")
        return False

    files = resolve_dependencies(component_names, COMPONENT_REGISTRY)
    if not files:
        print("No files to copy.")
        return False

    for rel in files:
        src = source_root / rel
        dest = target_root / remap_dest(rel)

        if not src.exists():
            print(f"Warning: Source file {src} does not exist.")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        # ensure __init__.py chain exists up to components/ or blocks/
        current = dest.parent
        while current != target_root:
            init = current / "__init__.py"
            if not init.exists():
                init.touch()
            if current.name in ("components", "blocks"):
                break
            current = current.parent

        shutil.copy2(src, dest)
        print(f"✓ Added {remap_dest(rel)}")

    return True


def _inject_into_plugins_kw(lines: list[str], call: ast.Call, snippet: str) -> bool:
    for i in range(call.lineno - 1, call.end_lineno or call.lineno):
        if "plugins=" in lines[i]:
            lines[i] = lines[i].replace("plugins=[", f"plugins=[\n{snippet},")
            return True
    return False


def _inject_new_plugins_arg(lines: list[str], call: ast.Call, snippet: str) -> bool:
    for i in range(call.lineno - 1, call.end_lineno or call.lineno):
        if "Config(" in lines[i] or "config(" in lines[i]:
            indent = " " * (len(lines[i]) - len(lines[i].lstrip()))
            lines[i] = lines[i].replace(
                "(",
                f"(\n{indent}    plugins=[\n{snippet}\n{indent}    ],",
            )
            return True
    return False


def _is_rx_config_call(call: ast.expr) -> TypeGuard[ast.Call]:
    return (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr.lower() == "config"
        and getattr(call.func.value, "id", "") == "rx"
    )


def _inject_via_ast(content: str, snippet: str) -> str | None:
    """Return patched content, or None if no rx.Config assignment was patched."""
    lines = content.splitlines()
    for node in ast.walk(ast.parse(content)):
        if not isinstance(node, ast.Assign) or not _is_rx_config_call(node.value):
            continue
        call = node.value
        has_plugins = any(kw.arg == "plugins" for kw in call.keywords)
        inject = _inject_into_plugins_kw if has_plugins else _inject_new_plugins_arg
        if inject(lines, call, snippet):
            patched = "\n".join(lines)
            patched = patched.replace("rx.plugins.TailwindV4Plugin(),", "")
            patched = patched.replace("rx.plugins.TailwindV4Plugin()", "")
            return patched.replace(",,", ",")
    return None


def _append_plugins_fallback(content: str, snippet: str) -> str | None:
    for name in ("rx.Config(", "rx.config("):
        if name in content:
            return content.replace(
                name,
                f"{name}\n    plugins=[\n{snippet}\n    ],",
            )
    return None


def patch_rxconfig(config_path: Path) -> None:
    """Inject TailwindV4 plugin into rxconfig.py if not already present."""
    content = config_path.read_text()

    if "var(--background)" in content:
        print("• rxconfig.py already contains Buridan UI theme tokens.")
        return

    try:
        snippet = TAILWIND_CONFIG_SNIPPET.strip().rstrip(",")
        patched = _inject_via_ast(content, snippet)
        if patched is None:
            patched = _append_plugins_fallback(content, snippet)

        if patched is None:
            print(
                "Warning: Could not automatically update rxconfig.py. Please configure manually.",
            )
            return

        import_stmt = "from reflex.plugins.shared_tailwind import TailwindConfig"
        if import_stmt not in patched:
            patched = f"{import_stmt}\n{patched}"
        config_path.write_text(patched)
        print("✓ Updated rxconfig.py with Buridan UI Tailwind config.")

    except Exception as e:  # noqa: BLE001 - best-effort config edit; fall back to manual instructions
        print(f"Warning: Could not parse rxconfig.py ({e}). Please configure manually.")


# ── commands ──────────────────────────────────────────────────────────────────


def cmd_init() -> None:
    """Initialize Buridan UI utilities in an existing Reflex project.

    - Locates or creates assets/globals.css
    - Appends CSS utilities (shimmer, scrollbar) if not already present
    - Updates rxconfig.py with TailwindV4 plugin config
    """
    root = Path.cwd()

    if not (root / "rxconfig.py").exists():
        print(
            "Error: rxconfig.py not found. Please run this command in a Reflex project root.",
        )
        sys.exit(1)

    # ── ensure assets/globals.css exists ─────────────────────────────────────
    assets_dir = root / "assets"
    assets_dir.mkdir(exist_ok=True)
    css_path = assets_dir / "globals.css"

    if not css_path.exists():
        css_path.write_text("")
        print(f"✓ Created {css_path.relative_to(root)}")
    else:
        print(f"• Found {css_path.relative_to(root)}")

    # ── append utilities that aren't already present ──────────────────────────
    current_css = css_path.read_text()
    added: list[str] = []

    for name, css in UTILITIES_BUNDLE:
        sentinel = UTILITY_SENTINELS[name]
        if sentinel in current_css:
            print(f"• {name} utility already present in globals.css — skipping.")
        else:
            current_css += f"\n{css}"
            added.append(name)

    if added:
        css_path.write_text(current_css)
        for name in added:
            print(f"✓ Added {name} utility to globals.css")

    # ── patch rxconfig.py ─────────────────────────────────────────────────────
    patch_rxconfig(root / "rxconfig.py")

    # ── next steps ────────────────────────────────────────────────────────────
    print("\n✓ Buridan UI initialized successfully.")
    print("\nNext steps:")
    print("  1. Add globals.css to your app stylesheets:")
    print('     app = rx.App(stylesheets=["globals.css"])')
    print("  2. Apply a theme:")
    print("     buridan apply --preset b0")
    print("  3. Add components:")
    print("     buridan add button")


def _consume_radius_scale_block(lines: list[str], end_line: int) -> int:
    """If a `@theme inline { ... }` block defining `--radius-sm` immediately
    follows `end_line` (skipping blank lines), return the index of its closing
    brace; otherwise return `end_line` unchanged.

    Only the radius scale block emitted by ``generate_theme_css`` is consumed
    — other ``@theme inline`` blocks (e.g. shimmer/scrollbar keyframes) do not
    define ``--radius-sm`` and are left untouched.
    """
    i = end_line + 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or not lines[i].strip().startswith("@theme inline {"):
        return end_line

    brace_depth = 0
    started = False
    seen_radius_sm = False
    for j in range(i, len(lines)):
        line = lines[j]
        if "--radius-sm" in line:
            seen_radius_sm = True
        brace_depth += line.count("{") - line.count("}")
        if brace_depth > 0:
            started = True
        if started and brace_depth == 0:
            return j if seen_radius_sm else end_line
    return end_line


def _find_block_end(lines: list[str], start: int) -> int | None:
    """Index of the line closing the brace block that opens at/after `start`."""
    depth = 0
    started = False
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth > 0:
            started = True
        if started and depth == 0:
            return i
    return None


def _theme_block_end(lines: list[str], start_line: int) -> int:
    """Index of the last line of the :root block, the `.dark` block after it
    (if any) and a trailing radius scale block (if any).
    """
    end_line = _find_block_end(lines, start_line)
    if end_line is None:
        return _consume_radius_scale_block(lines, start_line)
    for j in range(end_line + 1, len(lines)):
        if lines[j].strip().startswith(".dark {"):
            dark_end = _find_block_end(lines, j)
            if dark_end is not None and dark_end > j:
                end_line = dark_end
            break
    # also consume a trailing `@theme inline` radius scale block previously
    # emitted by generate_theme_css(), so re-applying a preset does not leave a
    # stale/duplicate radius block.
    return _consume_radius_scale_block(lines, end_line)


def _merge_theme_css(current: str, theme_css: str) -> str:
    if ":root {" not in current:
        return theme_css + "\n\n" + current
    lines = current.splitlines()
    start_line = next(
        (i for i, line in enumerate(lines) if line.strip().startswith(":root {")),
        None,
    )
    if start_line is None:
        return theme_css + "\n\n" + current
    end_line = _theme_block_end(lines, start_line)
    before = "\n".join(lines[:start_line]).rstrip("\n")
    after = "\n".join(lines[end_line + 1 :]).lstrip("\n")
    parts = [p for p in (before, theme_css, after) if p]
    return "\n\n".join(parts) + "\n"


def cmd_apply(preset: str) -> None:
    """Apply a theme preset to the project.

    Decodes the preset seed and writes :root / .dark CSS variables
    to assets/globals.css, preserving any existing utility blocks.
    """
    root = Path.cwd()

    if not (root / "rxconfig.py").exists():
        print("Error: rxconfig.py not found. Please run this in a Reflex project root.")
        sys.exit(1)

    config = decode_seed(preset)
    if not config:
        print(
            f"Error: Invalid preset ID '{preset}'. Get a valid preset from https://buridan-ui.com/create",
        )
        sys.exit(1)

    assets_dir = root / "assets"
    assets_dir.mkdir(exist_ok=True)
    css_path = assets_dir / "globals.css"

    theme_css = generate_theme_css(preset)
    if css_path.exists():
        css_path.write_text(_merge_theme_css(css_path.read_text(), theme_css))
    else:
        css_path.write_text(theme_css)

    print(f"✓ Applied preset '{preset}' to globals.css")
    print("\nNext steps:")
    print("  Add globals.css to your app stylesheets if you haven't already:")
    print('  app = rx.App(stylesheets=["globals.css"])')


def cmd_create() -> None:
    """Open the Buridan UI theme builder in the browser."""
    import webbrowser

    url = "https://buridan.reflex.run/create"
    print(f"Opening theme builder: {url}")
    webbrowser.open(url)


def cmd_add(component_names: list[str]) -> None:
    """Add one or more components and their dependencies to the project."""
    css_path = Path.cwd() / "assets" / "globals.css"
    if not css_path.exists() or ":root {" not in css_path.read_text():
        print("⚠  Warning: No theme detected in assets/globals.css.")
        print(
            "   Components use CSS variables that require a theme to render correctly.",
        )
        print("   Run 'buridan apply --preset b0' to apply a default theme.\n")

    if not add_components_to_project(component_names):
        sys.exit(1)


def cmd_list() -> None:
    """List all available components."""
    skip = {"core", "hugeicon"}
    names = sorted(n for n in COMPONENT_REGISTRY if n not in skip)
    print(f"Available components ({len(names)}):\n")
    for name in names:
        print(f"  {name}")


# ── entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="buridan",
        description="Buridan UI — CLI for Reflex component library",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize Buridan UI utilities in a Reflex project")

    # create
    sub.add_parser("create", help="Open the Buridan UI theme builder in your browser")

    # apply
    apply_p = sub.add_parser(
        "apply",
        help="Apply a theme preset (from buridan-ui.com/create)",
    )
    apply_p.add_argument(
        "--preset",
        required=True,
        help="Preset ID e.g. b0 or b2D0wqNxT",
    )

    # add
    add_p = sub.add_parser("add", help="Add components to your project")
    add_p.add_argument("components", nargs="+", help="Component name(s) to add")

    # list
    sub.add_parser("list", help="List all available components")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create()
    elif args.command == "init":
        cmd_init()
    elif args.command == "apply":
        cmd_apply(args.preset)
    elif args.command == "add":
        cmd_add(args.components)
    elif args.command == "list":
        cmd_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
