---
title: "Tooltip"
description: "A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it."
order: 27
---

# Tooltip

A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.

## Installation

Copy the following code into your app directory.

--INSTALL(tooltip)--

## Usage

--USAGE(tooltip)--

`tooltip.trigger()` forwards its default centering classes to custom `render_` targets. Pass `unstyled=True` to omit those defaults while keeping any caller-supplied `class_name`.

Tooltip open/close timing is not configurable on `tooltip.root()`: in `@base-ui/react` the delays live on `Tooltip.Provider` (group-wide) and `Tooltip.Trigger` (per-trigger), not on `Tooltip.Root`. Configure it group-wide via `tooltip.provider(delay=..., close_delay=...)`, or per-trigger via `tooltip.trigger(delay=..., close_delay=...)`.

## Anatomy 
Use the following composition to build a `Tooltip` component.
--ANATOMY(tooltip)--


## Examples


## General

A simple tooltip example. Use the `delay` prop to change how fast the tooltip shows.
--DEMO(tooltip_general)--

## Side
Use the `side` prop in `tooltip.positioner()` to change the position of the tooltip.
--DEMO(tooltip_sides)--
