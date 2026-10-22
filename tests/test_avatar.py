# noqa: INP001
"""Regression tests for the Avatar component's ``unstyled`` contract.

Mirrors ``tests/test_kbd.py`` (PR #112) and ``tests/test_tooltip.py``: every
avatar building block inherits ``unstyled: Var[bool]`` from ``CoreComponent``
and must honor it via ``CoreComponent.set_class_name`` — ``unstyled=True``
drops the default Tailwind classes and keeps only the caller's
``class_name``; a ``Var[bool]`` emits an ``rx.cond`` toggle selecting the
caller's class when the Var is true and the merged defaults otherwise.

Before the fix, every avatar ``create()`` popped ``class_name`` and
hard-merged defaults via ``cn(ClassNames.X, custom_classes)``, bypassing
``set_class_name`` entirely — so ``unstyled`` was swallowed (and later
stripped by ``_exclude_props``) with no effect on styling. Avatar
originally shipped (v0.9.0, commit 7d27209) calling ``set_class_name``; the
"components (I)" refactor (commit 58be251) mechanically rewrote the merge
and dropped ``unstyled`` support as a side effect.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import reflex as rx  # noqa: E402

from components.ui.avatar import (  # noqa: E402
    AvatarBadge,
    AvatarFallback,
    AvatarGroup,
    AvatarGroupCount,
    AvatarImage,
    AvatarRoot,
    ClassNames,
)


class _UnstyledState(rx.State):  # pyright: ignore[reportUntypedBaseClass]
    """State exposing a boolean Var for the dynamic ``unstyled`` escape hatch."""

    flag: bool = False


# ---------------------------------------------------------------------------
# AvatarRoot — defaults, merge, unstyled, dynamic Var, size, render_
# ---------------------------------------------------------------------------


def test_avatar_root_uses_default_classes() -> None:
    root = AvatarRoot.create("X")

    assert ClassNames.ROOT in str(root.class_name)


def test_avatar_root_merges_custom_class_name() -> None:
    root = AvatarRoot.create("X", class_name="custom-root")

    assert ClassNames.ROOT in str(root.class_name)
    assert "custom-root" in str(root.class_name)


def test_avatar_root_unstyled_omits_default_classes() -> None:
    root = AvatarRoot.create("X", unstyled=True)

    assert str(root.class_name) == ""


def test_avatar_root_unstyled_keeps_custom_class_name() -> None:
    root = AvatarRoot.create("X", class_name="custom-root", unstyled=True)

    assert str(root.class_name) == "custom-root"


def test_avatar_root_defaults_data_slot_and_size() -> None:
    root = AvatarRoot.create("X")

    rendered_props = " ".join(root.render()["props"])

    assert '"data-slot":"avatar"' in rendered_props
    assert '"data-size":"default"' in rendered_props


def test_avatar_root_preserves_explicit_size() -> None:
    root = AvatarRoot.create("X", size="lg")

    assert '"data-size":"lg"' in " ".join(root.render()["props"])


def test_avatar_root_var_unstyled_toggles_classes_dynamically() -> None:
    root = AvatarRoot.create(
        "X",
        class_name="custom-root",
        unstyled=_UnstyledState.flag,
    )
    class_name = str(root.class_name)

    # The class_name is gated on the Var via a ternary (rx.cond), not stripped.
    assert "?" in class_name
    # The caller's class survives in both branches of the toggle.
    assert "custom-root" in class_name
    # The default classes appear in the merged (false) branch.
    assert ClassNames.ROOT in class_name


def test_avatar_root_var_unstyled_without_custom_class_still_merges_defaults() -> None:
    root = AvatarRoot.create("X", unstyled=_UnstyledState.flag)

    assert ClassNames.ROOT in str(root.class_name)
    assert "?" in str(root.class_name)


def test_avatar_root_render_skips_default_class_merge() -> None:
    """``render_`` is a full-replacement escape hatch: ``set_class_name`` early-returns
    when ``render_`` is present and ``_merge_default_classes_with_render`` is False
    (the default for avatar), so the default ``ClassNames.ROOT`` is never merged onto
    the element — parity with ``TooltipPopup``. The caller's ``class_name`` survives
    unchanged.
    """
    root = AvatarRoot.create(
        render_=rx.el.div("x"),
        class_name="custom-root",
    )
    rendered_props = " ".join(root.render()["props"])

    assert ClassNames.ROOT not in rendered_props
    assert "custom-root" in rendered_props
    assert "render:" in rendered_props


def test_avatar_root_render_without_class_name_yields_no_class() -> None:
    root = AvatarRoot.create(render_=rx.el.div("x"))

    assert root.class_name is None
    assert ClassNames.ROOT not in " ".join(root.render()["props"])


# ---------------------------------------------------------------------------
# AvatarImage
# ---------------------------------------------------------------------------


def test_avatar_image_uses_default_classes() -> None:
    image = AvatarImage.create(src="https://example.com/x.png")

    assert ClassNames.IMAGE in str(image.class_name)


def test_avatar_image_merges_custom_class_name() -> None:
    image = AvatarImage.create(
        src="https://example.com/x.png",
        class_name="custom-image",
    )

    assert ClassNames.IMAGE in str(image.class_name)
    assert "custom-image" in str(image.class_name)


def test_avatar_image_unstyled_omits_default_classes() -> None:
    image = AvatarImage.create(src="https://example.com/x.png", unstyled=True)

    assert str(image.class_name) == ""


def test_avatar_image_unstyled_keeps_custom_class_name() -> None:
    image = AvatarImage.create(
        src="https://example.com/x.png",
        class_name="custom-image",
        unstyled=True,
    )

    assert str(image.class_name) == "custom-image"


def test_avatar_image_render_skips_default_class_merge() -> None:
    image = AvatarImage.create(render_=rx.el.img(src="https://example.com/x.png"))

    assert image.class_name is None
    assert ClassNames.IMAGE not in " ".join(image.render()["props"])


# ---------------------------------------------------------------------------
# AvatarFallback
# ---------------------------------------------------------------------------


def test_avatar_fallback_uses_default_classes() -> None:
    fallback = AvatarFallback.create("AB")

    assert ClassNames.FALLBACK in str(fallback.class_name)


def test_avatar_fallback_merges_custom_class_name() -> None:
    fallback = AvatarFallback.create("AB", class_name="custom-fallback")

    assert ClassNames.FALLBACK in str(fallback.class_name)
    assert "custom-fallback" in str(fallback.class_name)


def test_avatar_fallback_unstyled_omits_default_classes() -> None:
    fallback = AvatarFallback.create("AB", unstyled=True)

    assert str(fallback.class_name) == ""


def test_avatar_fallback_unstyled_keeps_custom_class_name() -> None:
    fallback = AvatarFallback.create("AB", class_name="custom-fallback", unstyled=True)

    assert str(fallback.class_name) == "custom-fallback"


def test_avatar_fallback_render_skips_default_class_merge() -> None:
    fallback = AvatarFallback.create(render_=rx.el.div("AB"))

    assert fallback.class_name is None
    assert ClassNames.FALLBACK not in " ".join(fallback.render()["props"])


# ---------------------------------------------------------------------------
# AvatarBadge
# ---------------------------------------------------------------------------


def test_avatar_badge_uses_default_classes() -> None:
    badge = AvatarBadge.create()

    assert ClassNames.BADGE in str(badge.class_name)


def test_avatar_badge_merges_custom_class_name() -> None:
    badge = AvatarBadge.create(class_name="custom-badge")

    assert ClassNames.BADGE in str(badge.class_name)
    assert "custom-badge" in str(badge.class_name)


def test_avatar_badge_unstyled_omits_default_classes() -> None:
    badge = AvatarBadge.create(unstyled=True)

    assert str(badge.class_name) == ""


def test_avatar_badge_unstyled_keeps_custom_class_name() -> None:
    badge = AvatarBadge.create(class_name="custom-badge", unstyled=True)

    assert str(badge.class_name) == "custom-badge"


# ---------------------------------------------------------------------------
# AvatarGroup
# ---------------------------------------------------------------------------


def test_avatar_group_uses_default_classes() -> None:
    group = AvatarGroup.create()

    assert ClassNames.GROUP in str(group.class_name)


def test_avatar_group_merges_custom_class_name() -> None:
    group = AvatarGroup.create(class_name="custom-group")

    assert ClassNames.GROUP in str(group.class_name)
    assert "custom-group" in str(group.class_name)


def test_avatar_group_unstyled_omits_default_classes() -> None:
    group = AvatarGroup.create(unstyled=True)

    assert str(group.class_name) == ""


def test_avatar_group_unstyled_keeps_custom_class_name() -> None:
    group = AvatarGroup.create(class_name="custom-group", unstyled=True)

    assert str(group.class_name) == "custom-group"


# ---------------------------------------------------------------------------
# AvatarGroupCount
# ---------------------------------------------------------------------------


def test_avatar_group_count_uses_default_classes() -> None:
    count = AvatarGroupCount.create("99")

    assert ClassNames.GROUP_COUNT in str(count.class_name)


def test_avatar_group_count_merges_custom_class_name() -> None:
    count = AvatarGroupCount.create("99", class_name="custom-count")

    assert ClassNames.GROUP_COUNT in str(count.class_name)
    assert "custom-count" in str(count.class_name)


def test_avatar_group_count_unstyled_omits_default_classes() -> None:
    count = AvatarGroupCount.create("99", unstyled=True)

    assert str(count.class_name) == ""


def test_avatar_group_count_unstyled_keeps_custom_class_name() -> None:
    count = AvatarGroupCount.create("99", class_name="custom-count", unstyled=True)

    assert str(count.class_name) == "custom-count"


# ---------------------------------------------------------------------------
# Parity with the kbd precedent (PR #112) — dynamic Var unstyled on a non-root
# component, mirroring the contract exercised by test_tooltip_var_unstyled_*.
# ---------------------------------------------------------------------------


def test_avatar_badge_var_unstyled_toggles_classes_dynamically() -> None:
    badge = AvatarBadge.create(class_name="custom-badge", unstyled=_UnstyledState.flag)
    class_name = str(badge.class_name)

    assert "?" in class_name
    assert "custom-badge" in class_name
    assert ClassNames.BADGE in class_name


# ---------------------------------------------------------------------------
# `unstyled` must not leak into the rendered DOM props (CoreComponent._exclude_props).
# ---------------------------------------------------------------------------


def test_avatar_root_unstyled_not_rendered_to_dom() -> None:
    root = AvatarRoot.create("X", class_name="custom-root", unstyled=True)
    rendered_props = " ".join(root.render()["props"])

    assert "unstyled" not in rendered_props
    assert '"data-slot":"avatar"' in rendered_props
    assert "custom-root" in rendered_props
