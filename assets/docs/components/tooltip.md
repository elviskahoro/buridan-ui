

# Tooltip

A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.

## Installation

Copy the following code into your app directory.


> **Error: 'tooltip' not found in registry**


## Usage


> **Error: 'tooltip' not found in registry**


`tooltip.trigger()` forwards its default centering classes to custom `render_` targets. Pass `unstyled=True` to omit those defaults while keeping any caller-supplied `class_name`.

## Anatomy 
Use the following composition to build a `Tooltip` component.

```python
tooltip.root(
    tooltip.trigger(),
    tooltip.portal(
        tooltip.positioner(
            tooltip.popup(
                tooltip.arrow(),
                "Tooltip content",
            ),
        ),
    ),
)
```



## Examples


## General

A simple tooltip example. Use the `delay` prop to change how fast the tooltip shows.

> **Error: 'tooltip_general' not found in registry**


## Side
Use the `side` prop in `tooltip.positioner()` to change the position of the tooltip.

> **Error: 'tooltip_sides' not found in registry**

