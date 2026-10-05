---
title: "Dialog"
description: "A window overlaid on either the primary window or another dialog window, rendering the content underneath inert."
order: 8
---

# Dialog

A window overlaid on either the primary window or another dialog window, rendering the content underneath inert.

# Installation

Copy the following code into your app directory.

--INSTALL(dialog)--

# Usage

--USAGE(dialog)--

# Anatomy 
Use the following composition to build a `Dialog` component.

--ANATOMY(dialog)--

# Examples

## Custom Close Button

`render_` replaces the close control, including its default classes. To create a custom top-right close icon, pass `dialog.class_names.CLOSE` to the rendered button; footer close buttons can use their own styling without those positioning classes.

--DEMO(dialog_close_button)--

## No Close Button

To omit the top-right close cross icon from your dialog layout, simply exclude the `dialog.close()` sub-component containing the icon button from your composition tree.

--DEMO(dialog_no_close_button)--

## Sticky Footer

Keep actions visible while the content scrolls.

--DEMO(dialog_sticky_footer)--
