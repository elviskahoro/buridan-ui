import inspect
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.www.library.getting_started.clientstate_components import (  # noqa: E402
    form_state_pattern_example,
)


def test_form_state_pattern_merges_username_into_existing_client_state() -> None:
    component = form_state_pattern_example()

    on_change = component.event_triggers["on_change"].events[0]
    expression = on_change._js_expr

    # The current form-state object is spread before the username field is updated.
    assert re.search(
        r"\.\.\.\s*refs\[\s*['\"]_client_state_dict_form['\"]\s*\]",
        expression,
    )
    assert re.search(r"\[\s*['\"]username['\"]\s*\]", expression)


def test_demo_uses_only_the_referenced_function_source(monkeypatch) -> None:
    from app.www import parser as parser_module
    from app.www.parser import DocParser

    captured = {}

    def capture_demo_source(component, source: str):
        captured["source"] = source
        return component

    monkeypatch.setattr(parser_module, "demo_wrapper", capture_demo_source)
    parser = DocParser(
        registry={
            "form_state_pattern_example": (
                form_state_pattern_example,
                "form_state_pattern_example",
            )
        }
    )

    parser._render("demo", "form_state_pattern_example")

    expected_source = inspect.getsource(form_state_pattern_example).strip()
    assert captured["source"] == expected_source
    assert "tab_navigation_example" not in captured["source"]
