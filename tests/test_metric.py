# noqa: INP001
# pyright: reportUnknownMemberType=false
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.metric import MetricRoot, metric  # noqa: E402


def test_metric_returns_metric_root_instance() -> None:
    rendered = metric(label="Revenue", value="$12,345")

    assert isinstance(rendered, MetricRoot)


def test_metric_renders_label_and_value() -> None:
    rendered = str(metric(label="Revenue", value="$12,345").render())

    assert "Revenue" in rendered
    assert "$12,345" in rendered
    assert "shadow-sm" in rendered


def test_metric_without_trend_omits_trend_text() -> None:
    rendered = str(metric(label="Revenue", value="$12,345").render())

    assert "+12%" not in rendered


def test_metric_with_trend_renders_trend_text() -> None:
    rendered = str(metric(label="Revenue", value="$12,345", trend="+12%").render())

    assert "+12%" in rendered


def test_metric_root_accepts_arbitrary_children_directly() -> None:
    root = metric.root(class_name="custom-root")

    assert isinstance(root, MetricRoot)
    assert "custom-root" in str(root.class_name)
