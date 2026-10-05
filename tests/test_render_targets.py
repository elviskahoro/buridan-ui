"""Regression coverage for default classes forwarded to custom render targets."""

import reflex as rx

from components.ui.accordion import (
    AccordionTrigger,
    ClassNames as AccordionClassNames,
)
from components.ui.dialog import ClassNames as DialogClassNames, DialogClose


def test_accordion_trigger_keeps_styled_render_target_unchanged() -> None:
    target = rx.el.button("toggle", class_name="custom-accordion-trigger")
    trigger = AccordionTrigger.create(render_=target, class_name="caller-class")
    rendered_tree = str(trigger.render())

    assert AccordionClassNames.TRIGGER not in rendered_tree
    assert "custom-accordion-trigger" in rendered_tree
    assert "caller-class" in rendered_tree
    assert "render:" in rendered_tree


def test_dialog_close_keeps_styled_render_target_unchanged() -> None:
    target = rx.el.button("close", class_name="custom-dialog-close")
    close = DialogClose.create(render_=target)
    rendered_tree = str(close.render())

    assert DialogClassNames.CLOSE not in rendered_tree
    assert "custom-dialog-close" in rendered_tree
    assert "render:" in rendered_tree


def test_dialog_close_preserves_caller_classes_with_render_target() -> None:
    close = DialogClose.create(
        render_=rx.el.button("cancel"), class_name="flex-1", unstyled=True
    )
    rendered_tree = str(close.render())

    assert DialogClassNames.CLOSE not in rendered_tree
    assert "flex-1" in rendered_tree
