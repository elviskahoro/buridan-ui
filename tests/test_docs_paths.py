import importlib
import os
from pathlib import Path

import pytest
from PIL import ImageFont

from app.www import constants
from app.www.generator import generate_docs_library
from app.www.parser import DocParser


def test_docs_generation_is_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("BURIDAN_DEV_MODE", raising=False)

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


@pytest.mark.parametrize("absolute", [True, False])
def test_parser_rejects_load_directories_outside_project_root(
    tmp_path, absolute
):
    project_root = Path(constants.__file__).resolve().parents[2]
    load_dir = tmp_path if absolute else os.path.relpath(tmp_path, project_root)

    with pytest.raises(ValueError, match="resolves outside project root"):
        DocParser(dynamic_load_dirs=[str(load_dir)])


def test_preview_cards_use_repository_paths_from_another_working_directory(
    monkeypatch, tmp_path
):
    default_font = ImageFont.load_default()
    monkeypatch.setattr(
        ImageFont, "truetype", lambda *_args, **_kwargs: default_font
    )
    preview_cards = importlib.import_module("scripts.generate_preview_cards")
    generated_paths = []
    monkeypatch.setattr(
        preview_cards,
        "create_social_card",
        lambda title, description, output_path: generated_paths.append(output_path),
    )
    monkeypatch.chdir(tmp_path)

    preview_cards.generate_social_cards()

    assert generated_paths
    assert all(
        path.parent == Path(__file__).resolve().parents[1] / "assets" / "social"
        for path in generated_paths
    )
