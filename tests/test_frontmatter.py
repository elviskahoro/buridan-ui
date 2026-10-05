import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.frontmatter import parse_frontmatter  # noqa: E402


@pytest.mark.parametrize(
    ("order_value", "expected"),
    [
        ("-1", -1),
        ("-5", -5),
        ("+5", 5),
        ("5", 5),
        ("0", 0),
        ("007", 7),
        ("1_000", "1_000"),
        ("1.5", "1.5"),
        ("first", "first"),
        ("٥", "٥"),
        ("５", "５"),
        ("+", "+"),
    ],
)
def test_parse_frontmatter_order_value(order_value: str, expected: int | str) -> None:
    content = f"---\ntitle: Test\norder: {order_value}\n---\nBody\n"

    metadata, body = parse_frontmatter(content)

    assert metadata["order"] == expected
    assert type(metadata["order"]) is type(expected)
    assert body == "Body\n"


def test_generate_doc_routes_sorts_mixed_order_values_deterministically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.utils import routes

    docs_dir = tmp_path / "docs"
    section_dir = docs_dir / "section"
    section_dir.mkdir(parents=True)
    (section_dir / "later.md").write_text(
        "---\ntitle: Later\ndescription: Later page\norder: 5\n---\n",
        encoding="utf-8",
    )
    (section_dir / "first.md").write_text(
        "---\ntitle: First\ndescription: First page\norder: -1\n---\n",
        encoding="utf-8",
    )
    (section_dir / "last.md").write_text(
        "---\ntitle: Last\ndescription: Last page\norder: last\n---\n",
        encoding="utf-8",
    )
    (section_dir / "alpha.md").write_text(
        "---\ntitle: Alpha\ndescription: Alpha page\norder: alpha\n---\n",
        encoding="utf-8",
    )
    (section_dir / "default.md").write_text(
        "---\ntitle: Default\ndescription: Default page\n---\n",
        encoding="utf-8",
    )
    (section_dir / "zero_b.md").write_text(
        "---\ntitle: Zero B\ndescription: Zero page B\norder: 0\n---\n",
        encoding="utf-8",
    )
    (section_dir / "zero_a.md").write_text(
        "---\ntitle: Zero A\ndescription: Zero page A\norder: 0\n---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes.constants, "DOCS_BASE_DIR", docs_dir)

    result = routes.generate_doc_routes("section", "docs/section/")

    assert [route["title"] for route in result] == [
        "First",
        "Default",
        "Zero A",
        "Zero B",
        "Later",
        "Alpha",
        "Last",
    ]
    assert [route["order"] for route in result] == [
        -1,
        0,
        0,
        0,
        5,
        "alpha",
        "last",
    ]
