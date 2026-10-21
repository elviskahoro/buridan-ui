import ast
import importlib
import inspect
import pathlib
import re
import shutil
import sys
from collections.abc import Callable
from typing import Any

# Add the project root to the Python path to allow imports
ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# --- PATHS ---
DOCS_SOURCE_DIR = ROOT_DIR / "docs"
MARKDOWN_OUTPUT_DIR = ROOT_DIR / "assets" / "docs"
DYNAMIC_LOAD_DIRS = ["app/www/library", "components/ui"]

# Maps lowercased names to (object, name as defined) for every loaded callable.
Registry = dict[str, tuple[Callable[..., Any], str]]


def dynamic_load_components(dirs: list[str]) -> Registry:
    """Dynamically loads component functions and classes from given directories."""
    registry: Registry = {}
    for d in dirs:
        dir_path = ROOT_DIR / d
        if not dir_path.exists():
            print(f"Warning: Directory not found: {dir_path}")
            continue

        for py_file in dir_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            relative_py_file = py_file.relative_to(ROOT_DIR)
            module_path = ".".join(relative_py_file.with_suffix("").parts)

            try:
                module = importlib.import_module(module_path)
                # First, identify objects defined in this module
                for name, obj in inspect.getmembers(module):
                    if (
                        hasattr(obj, "__module__") and obj.__module__ == module.__name__
                    ) or (
                        # Handle cases where __module__ might be different but it's defined here
                        # or it's a ComponentNamespace
                        getattr(obj, "__module__", None) == module.__name__
                    ):
                        # Check if it's a function, class, method, or callable assigned to a name
                        if (
                            inspect.isfunction(obj)
                            or inspect.isclass(obj)
                            or inspect.ismethod(obj)
                            or callable(obj)
                        ):
                            registry[name.lower()] = (obj, name)
            except Exception as e:
                print(
                    f"Warning: Could not import from module {module_path}. Error: {e}",
                    file=sys.stderr,
                )
    return registry


MIN_TABLE_LINES = 2
MIN_SEPARATOR_WIDTH = 3


def align_markdown_tables(content: str) -> str:
    """Align pipes in markdown tables to meet MD060 requirements."""
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a table header (contains pipes)
        if line.strip().startswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1]
            # Check if next line is a separator (contains dashes and pipes)
            if "|" in next_line and all(
                c in "| -:" for c in next_line.replace(" ", "")
            ):
                # Collect all lines in this table
                table_lines = [line]
                j = i + 1
                while j < len(lines) and "|" in lines[j]:
                    table_lines.append(lines[j])
                    j += 1

                # Align the table
                aligned_table = align_table(table_lines)
                result.extend(aligned_table)
                i = j
                continue

        result.append(line)
        i += 1

    return "\n".join(result)


# Splits on cell delimiters but not on `\\|`, an escaped pipe inside a cell.
TABLE_CELL_DELIMITER = re.compile(r"(?<!\\)\|")


def _parse_table_rows(lines: list[str]) -> list[list[str]]:
    """Parse table lines into rows of cells."""
    return [
        [cell.strip() for cell in TABLE_CELL_DELIMITER.split(line)[1:-1]]
        for line in lines
    ]


def _calculate_col_widths(rows: list[list[str]]) -> list[int]:
    """Calculate the width needed for each column."""
    col_widths = []
    max_cols = max(len(row) for row in rows)
    for col_idx in range(max_cols):
        max_width = max(
            (len(row[col_idx]) for row in rows if col_idx < len(row)),
            default=0,
        )
        col_widths.append(max_width)
    return col_widths


def _format_table_row(cells: list[str], col_widths: list[int]) -> str:
    """Format a table row with aligned columns."""
    aligned_cells = [
        cell.ljust(col_widths[col_idx])
        for col_idx, cell in enumerate(cells)
        if col_idx < len(col_widths)
    ]
    return "| " + " | ".join(aligned_cells) + " |"


def _format_separator_cell(cell: str, width: int) -> str:
    """Pad a separator cell to width, keeping its `:` alignment markers."""
    left = cell.startswith(":")
    right = len(cell) > 1 and cell.endswith(":")
    dashes = "-" * (width - left - right)
    return (":" if left else "") + dashes + (":" if right else "")


def _format_table_separator(cells: list[str], col_widths: list[int]) -> str:
    """Format a table separator line."""
    sep_cells = [
        _format_separator_cell(cells[col_idx] if col_idx < len(cells) else "", width)
        for col_idx, width in enumerate(col_widths)
    ]
    return "| " + " | ".join(sep_cells) + " |"


def align_table(lines: list[str]) -> list[str]:
    """Align a markdown table's pipes for consistent column widths."""
    if not lines or len(lines) < MIN_TABLE_LINES:
        return lines

    header, separator, *body = _parse_table_rows(lines)
    # Separator cells need at least three dashes, so they set a minimum width.
    col_widths = [
        max(width, MIN_SEPARATOR_WIDTH)
        for width in _calculate_col_widths([header, *body])
    ]

    return [
        _format_table_row(header, col_widths),
        _format_table_separator(separator, col_widths),
        *(_format_table_row(row, col_widths) for row in body),
    ]


def _inspection_target(obj: Callable[..., Any]) -> Callable[..., Any]:
    """Use the class for inspection if obj is an instance (like ComponentNamespace)."""
    if inspect.isclass(obj) or inspect.isfunction(obj) or inspect.ismethod(obj):
        return obj
    return obj.__class__


def _module_source(obj: Callable[..., Any]) -> str:
    """Return the full source of the module that defines obj."""
    return pathlib.Path(inspect.getfile(obj)).read_text(encoding="utf-8")


def _anatomy_block(name: object) -> str:
    from app.registry.anatomy import ANATOMY

    src = ANATOMY.get(str(name).lower())
    if not src:
        return f"\n> **Error: No anatomy found for '{name}'**\n"
    return f"\n```python\n{src.strip()}\n```\n"


def _demo_block(name: object, obj: Callable[..., Any]) -> str:
    """Source code of the specific demo function."""
    try:
        src = inspect.getsource(obj)
    except (OSError, TypeError) as e:
        return f"\n> **Error getting source for {name}: {e}**\n"
    return f"\n```python\n{src.strip()}\n```\n"


def _code_block(cmd: str, name: object, obj: Callable[..., Any], language: str) -> str:
    try:
        src = (
            _module_source(_inspection_target(obj))
            if "_file" in cmd
            else inspect.getsource(obj)
        )
    except (OSError, TypeError) as e:
        return f"\n> **Error getting code for {name}: {e}**\n"
    return f"\n```{language}\n{src.strip()}\n```\n"


def _install_block(name: object, obj: Callable[..., Any], cli_cmd: str) -> str:
    try:
        module_src = _module_source(_inspection_target(obj))
    except (OSError, TypeError) as e:
        return f"\n> **Error processing install for {name}: {e}**\n"
    return (
        f"### CLI\n\n```bash\n{cli_cmd}\n```\n\n"
        f"### Manual Installation\n\n```python\n{module_src.strip()}\n```\n"
    )


def _usage_block(name: object, obj: Callable[..., Any], preferred_name: str) -> str:
    try:
        file_path = inspect.getfile(_inspection_target(obj))
    except TypeError as e:
        return f"\n> **Error processing usage for {name}: {e}**\n"
    module_stem = pathlib.Path(file_path).stem
    return (
        f"\n```python\nfrom components.ui.{module_stem} import {preferred_name}\n```\n"
    )


def _process_delimiter(match: re.Match[str], registry: Registry) -> str:
    """Process a single component delimiter match."""
    cmd = match.group(1).lower()
    arg = match.group(2)

    # Parse argument (handle strings or lists)
    try:
        val = (
            ast.literal_eval(arg)
            if arg and any(arg.startswith(c) for c in "[{'\"")
            else arg
        )
    except (ValueError, SyntaxError) as e:
        return f"\n> **Error in {cmd}: {e}**\n"
    name = val[0] if isinstance(val, list) else val
    # Optional second list item: code language or install CLI command.
    has_option = isinstance(val, list) and len(val) > 1
    option = val[1] if has_option else None

    if cmd == "anatomy":
        return _anatomy_block(name)

    registry_entry = registry.get(str(name).lower())
    if not registry_entry:
        return f"\n> **Error: '{name}' not found in registry**\n"
    obj, preferred_name = registry_entry

    if "demo" in cmd:
        return _demo_block(name, obj)
    if "code" in cmd:
        return _code_block(cmd, name, obj, option or "python")
    if cmd == "install":
        cli_cmd = (
            str(option) if has_option else f"buridan add component {str(name).lower()}"
        )
        return _install_block(name, obj, cli_cmd)
    if cmd == "usage":
        return _usage_block(name, obj, preferred_name)

    return f"\n> **Warning: Unknown command '{cmd}'**\n"


def convert_to_pure_markdown(content: str, registry: Registry) -> str:
    """Replaces custom component delimiters in markdown content with formatted code blocks."""
    delimiter_pattern = r"--([\w_]+)(?:\((.*)\))?--"

    # Remove frontmatter if present (consistent with generator.py)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) > 2:
            content = parts[2]

    def replacer(m: re.Match[str]) -> str:
        return _process_delimiter(m, registry)

    content = re.sub(delimiter_pattern, replacer, content)
    # Align markdown tables to meet MD060 requirements
    return align_markdown_tables(content)


def main() -> None:
    """Main function to generate pure markdown files from the docs directory."""
    print("Starting markdown generation process...")

    # Clean up old output directory
    if MARKDOWN_OUTPUT_DIR.exists():
        shutil.rmtree(MARKDOWN_OUTPUT_DIR)
        print(f"Cleaned up old output: {MARKDOWN_OUTPUT_DIR}")

    # Load components from all target directories
    print(f"Loading components from: {DYNAMIC_LOAD_DIRS}")
    component_registry = dynamic_load_components(DYNAMIC_LOAD_DIRS)
    print(f"Successfully loaded {len(component_registry)} objects into registry.")

    # Ensure output directory exists
    MARKDOWN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process markdown files
    print(f"Processing markdown files from: {DOCS_SOURCE_DIR}")
    file_count = 0
    for md_file in DOCS_SOURCE_DIR.rglob("*.md"):
        file_count += 1
        original_content = md_file.read_text()
        pure_md_content = convert_to_pure_markdown(original_content, component_registry)

        # Create new path with hyphens (e.g., getting_started -> getting-started)
        relative_path = md_file.relative_to(DOCS_SOURCE_DIR)
        hyphenated_parts = [part.replace("_", "-") for part in relative_path.parts]
        output_path = MARKDOWN_OUTPUT_DIR / pathlib.Path(*hyphenated_parts)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(pure_md_content)

        print(
            f"Processed: {md_file.relative_to(ROOT_DIR)} -> {output_path.relative_to(ROOT_DIR)}",
        )

    print(f"\nMarkdown generation complete. Processed {file_count} files.")


if __name__ == "__main__":
    main()
