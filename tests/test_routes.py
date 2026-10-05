import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import app.utils.routes as routes


def test_components_and_charts_preserve_generated_order(monkeypatch) -> None:
    generated_routes = {
        "getting_started": [],
        "utilities": [],
        "resources": [],
        "components": [
            {"title": "Typography", "order": 0},
            {"title": "Accordion", "order": 1},
        ],
        "charts": [
            {"title": "Zebra Chart", "order": 0},
            {"title": "Area Chart", "order": 1},
        ],
    }
    monkeypatch.setattr(
        routes,
        "generate_doc_routes",
        lambda section, _base_path: generated_routes[section],
    )

    result = routes.build_all_routes()

    assert result["components"] == generated_routes["components"]
    assert result["charts"] == generated_routes["charts"]


def test_resources_and_utilities_remain_sorted_by_title(monkeypatch) -> None:
    generated_routes = {
        "getting_started": [],
        "utilities": [
            {"title": "Zebra Utility", "order": 0},
            {"title": "Alpha Utility", "order": 1},
        ],
        "resources": [
            {"title": "Zebra Resource", "order": 0},
            {"title": "Alpha Resource", "order": 1},
        ],
        "components": [],
        "charts": [],
    }
    monkeypatch.setattr(
        routes,
        "generate_doc_routes",
        lambda section, _base_path: generated_routes[section],
    )

    result = routes.build_all_routes()

    assert [item["title"] for item in result["utilities"]] == [
        "Alpha Utility",
        "Zebra Utility",
    ]
    assert [item["title"] for item in result["resources"]] == [
        "Alpha Resource",
        "Zebra Resource",
    ]


def test_generate_doc_routes_sorts_by_frontmatter_order_and_url_ties(
    monkeypatch, tmp_path
) -> None:
    docs_path = tmp_path / "components"
    docs_path.mkdir()
    markdown = {
        "zulu.md": '---\ntitle: "Zulu"\ndescription: "Tie entry"\norder: 1\n---\n',
        "late.md": '---\ntitle: "Late"\ndescription: "Later entry"\norder: 2\n---\n',
        "default.md": '---\ntitle: "Default"\ndescription: "Default order"\n---\n',
        "alpha.md": '---\ntitle: "Alpha"\ndescription: "Tie entry"\norder: 1\n---\n',
        "aardvark.md": '---\ntitle: "Aardvark"\ndescription: "Default-order tie"\norder: 0\n---\n',
    }
    paths = []
    for filename, content in markdown.items():
        path = docs_path / filename
        path.write_text(content, encoding="utf-8")
        paths.append(path)

    # Reverse both tied URL groups to prove tie ordering ignores glob order.
    glob_order = [paths[2], paths[4], paths[0], paths[3], paths[1]]
    monkeypatch.setattr(routes.constants, "DOCS_BASE_DIR", tmp_path)
    monkeypatch.setattr(
        routes.glob,
        "glob",
        lambda _pattern, recursive: [str(path) for path in glob_order],
    )

    generated = routes.generate_doc_routes("components", "docs/components/")

    assert [item["title"] for item in generated] == [
        "Aardvark",
        "Default",
        "Alpha",
        "Zulu",
        "Late",
    ]
