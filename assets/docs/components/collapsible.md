

# Collapsible

An interactive component which expands/collapses a panel.

## Installation

Copy the following code into your app directory.


> **Error: 'collapsible' not found in registry**


## Usage


> **Error: 'collapsible' not found in registry**


Collapsible components treat `render_` as a full replacement: component defaults are not applied to the target. Add the desired layout classes to the rendered element itself.

## Anatomy 
Use the following composition to build a `Collapsible` component.


```python
collapsible.root(
    collapsible.trigger(),
    collapsible.panel(),
)
```


## Controlled State

Use the `open` and `on_open_change` props to control the state.

```python
import reflex as rx
from components.ui.collapsible import collapsible

class ControlledCollapsibleState(rx.State):
    is_open: bool = False

    def toggle_open(self, open_state: bool):
        self.is_open = open_state

def controlled_example() -> rx.Component:
    return collapsible.root(
        collapsible.trigger(Toggle),
        collapsible.panel("Content"),
        open=ControlledCollapsibleState.is_open,
        on_open_change=ControlledCollapsibleState.toggle_open,
    )
```

## Examples

## Basic


> **Error: 'collapsible_basic' not found in registry**


## Nested

Use nested collapsibles to build a file tree.


> **Error: 'collapsible_nested' not found in registry**


## Interactive


> **Error: 'collapsible_interactive' not found in registry**

