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


def test_client_state_guide_renders_live_demo_with_example_source() -> None:
    from app.www.constants import COMPONENTS_ROOT, DOCS_LIBRARY_ROOT
    from app.www.frontmatter import parse_frontmatter
    from app.www.parser import DocParser

    guide_path = ROOT_DIR / "docs/resources/client_state_var.md"
    _, markdown = parse_frontmatter(guide_path.read_text())
    parser = DocParser(dynamic_load_dirs=[DOCS_LIBRARY_ROOT, COMPONENTS_ROOT])

    components = parser.parse_and_render(markdown)
    demo = next(
        component
        for component in components
        if "form_state_pattern_example" in str(component)
    )
    rendered_demo = str(demo)

    assert "tab_navigation_example" not in rendered_demo
    assert "client_state_dict_form" in rendered_demo
    assert "username" in rendered_demo
