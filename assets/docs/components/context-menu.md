

# Context Menu

Displays a menu of actions triggered by a right click.

## Installation

Copy the following code into your app directory.


> **Error: 'context_menu' not found in registry**


## Usage


> **Error: 'context_menu' not found in registry**


## Anatomy 

Use the following composition to build a `Context Menu` component.


```python
context_menu.root(
    context_menu.trigger(),
    context_menu.portal(
        context_menu.positioner(
            context_menu.popup(
                context_menu.item(),
                context_menu.separator(),
                context_menu.group(
                    context_menu.group_label(),
                    context_menu.item(),
                ),
                context_menu.checkbox_item(
                    context_menu.checkbox_item_indicator(),
                ),
                context_menu.radio_group(
                    context_menu.radio_item(
                        context_menu.radio_item_indicator(),
                    ),
                ),
                context_menu.sub(
                    context_menu.sub_trigger(),
                    context_menu.portal(
                        context_menu.positioner(
                            context_menu.popup(),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
```


A Context Menu is built by composing a root trigger with an overlay surface.

```composition
context_menu.root
├── context_menu.trigger
└── context_menu.portal
    └── context_menu.positioner
        └── context_menu.popup
            ├── context_menu.group
            │   ├── context_menu.group_label
            │   ├── context_menu.item
            │   └── context_menu.item
            ├── context_menu.separator
            ├── context_menu.group
            │   ├── context_menu.group_label
            │   ├── context_menu.checkbox_item
            │   │   └── context_menu.checkbox_item_indicator
            │   └── context_menu.checkbox_item
            │       └── context_menu.checkbox_item_indicator
            ├── context_menu.separator
            ├── context_menu.group
            │   ├── context_menu.group_label
            │   └── context_menu.radio_group
            │       ├── context_menu.radio_item
            │       │   └── context_menu.radio_item_indicator
            │       └── context_menu.radio_item
            │           └── context_menu.radio_item_indicator
            └── context_menu.sub
                ├── context_menu.sub_trigger
                └── context_menu.portal
                    └── context_menu.positioner
                        └── context_menu.popup
                            └── context_menu.group
                                ├── context_menu.item
                                └── context_menu.item
```

## Examples

## Basic

A simple context menu with a few actions.


> **Error: 'context_menu_basic' not found in registry**


## Submenu

Use `context_menu.sub` to nest secondary actions.


> **Error: 'context_menu_submenu' not found in registry**


## Shortcuts

Use `context_menu.shortcut` to show keyboard hints.


> **Error: 'context_menu_shortcuts' not found in registry**


## Groups

Group related actions and separate them with dividers.


> **Error: 'context_menu_groups' not found in registry**


## Checkboxes

Use `context_menu.checkbox_item` for toggles.


> **Error: 'context_menu_checkboxes' not found in registry**


## Radio

Use `context_menu.radio_item` for exclusive choices.


> **Error: 'context_menu_radio' not found in registry**



## Sides

Control submenu placement with side and align props.


> **Error: 'context_menu_sides' not found in registry**

