from components.ui.button import BUTTON_VARIANTS


def test_icon_sm_rule_uses_14px_only_for_unsized_svgs() -> None:
    classes = BUTTON_VARIANTS["size"]["icon-sm"]

    assert "size-7" in classes
    assert "[&_svg:not([class*='size-'])]:size-3.5" in classes
