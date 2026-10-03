from pathlib import Path

from app.www import constants
from app.www.generator import generate_docs_library
from app.www.parser import DocParser


def test_docs_generation_is_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    assert constants.DOCS_BASE_DIR == Path(__file__).resolve().parents[1] / "docs"
    docs = generate_docs_library()

    assert docs
    assert any(doc.url == "docs/getting-started/introduction" for doc in docs)


def test_parser_loads_absolute_and_repo_relative_directories(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    parser = DocParser(
        dynamic_load_dirs=[constants.DOCS_LIBRARY_ROOT, constants.COMPONENTS_ROOT]
    )

    assert "accordion_basic" in parser.registry
    assert "accordionroot" in parser.registry
