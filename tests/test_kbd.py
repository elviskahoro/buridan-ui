import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from components.ui.kbd import ClassNames, KbdGroupContainer, KbdRoot


def test_kbd_root_uses_default_classes() -> None:
    root = KbdRoot.create("K")

    assert ClassNames.KBD in str(root.class_name)


def test_kbd_root_merges_custom_class_name() -> None:
    root = KbdRoot.create("K", class_name="custom-kbd")

    assert ClassNames.KBD in str(root.class_name)
    assert "custom-kbd" in str(root.class_name)


def test_kbd_root_unstyled_omits_default_classes() -> None:
    root = KbdRoot.create("K", unstyled=True)

    assert str(root.class_name) == ""


def test_kbd_root_unstyled_keeps_custom_class_name() -> None:
    root = KbdRoot.create("K", class_name="custom-kbd", unstyled=True)

    assert str(root.class_name) == "custom-kbd"


def test_kbd_group_uses_default_classes() -> None:
    group = KbdGroupContainer.create("K")

    assert ClassNames.GROUP in str(group.class_name)


def test_kbd_group_merges_custom_class_name() -> None:
    group = KbdGroupContainer.create("K", class_name="custom-grp")

    assert ClassNames.GROUP in str(group.class_name)
    assert "custom-grp" in str(group.class_name)


def test_kbd_group_unstyled_omits_default_classes() -> None:
    group = KbdGroupContainer.create("K", unstyled=True)

    assert str(group.class_name) == ""


def test_kbd_group_unstyled_keeps_custom_class_name() -> None:
    group = KbdGroupContainer.create("K", class_name="custom-grp", unstyled=True)

    assert str(group.class_name) == "custom-grp"
