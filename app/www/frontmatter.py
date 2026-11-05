import re
from typing import Any

# --- Simple frontmatter parser. ---
FRONTMATTER_PARTS = 3  # text before, frontmatter, body


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """A simple frontmatter parser."""
    metadata: dict[str, Any] = {}
    if not content.startswith("---"):
        return metadata, content

    parts = content.split("---", 2)
    if len(parts) < FRONTMATTER_PARTS:
        return metadata, content

    frontmatter = parts[1]
    rest_of_content = parts[2]

    for line in frontmatter.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]

            if key == "order" and re.fullmatch(r"[+-]?[0-9]+", value, re.ASCII):
                value = int(value)

            metadata[key] = value

    # print(metadata)

    return metadata, rest_of_content.lstrip()
