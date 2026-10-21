

# Menu

Displays a menu to the user — such as a set of actions or functions — triggered by a button.

## Installation

Copy the following code into your app directory.


> **Error: 'menu' not found in registry**


## Usage


> **Error: 'menu' not found in registry**


## Anatomy 
Use the following composition to build a `Menu` component.


```python
menu.root(
    menu.trigger(),
    menu.portal(
        menu.positioner(
            menu.popup(
                menu.item(),
                menu.separator(),
                menu.group(
                    menu.group_label(),
                    menu.item(),
                ),
                menu.checkbox_item(
                    menu.checkbox_item_indicator(),
                ),
                menu.radio_group(
                    menu.radio_item(
                        menu.radio_item_indicator(),
                    ),
                ),
                menu.submenu_root(
                    menu.submenu_trigger(),
                    menu.portal(
                        menu.positioner(
                            menu.popup(),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
```


## Example

## Basic

A basic dropdown menu with labels and separators.


> **Error: 'menu_basic' not found in registry**


## Submenu

Use `menu.submenu_root` to nest secondary actions.


> **Error: 'menu_submenu' not found in registry**


## Shortcuts

Add `menu.shortcut` to show keyboard hints.


> **Error: 'menu_shortcuts' not found in registry**


## Icons

Combine icons with labels for quick scanning.


> **Error: 'menu_icons' not found in registry**


## Checkboxes

Use `menu.checkbox_item` for toggles. 


> **Error: 'menu_checkboxes' not found in registry**


## Checkboxes Icons

Add icons to checkbox items.


> **Error: 'menu_checkboxes_icons' not found in registry**


## Radio Group

Use `menu.radio_group` for exclusive choices.


> **Error: 'menu_radio_group' not found in registry**


## Avatar 

An account switcher dropdown triggered by an avatar.


> **Error: 'menu_avatar' not found in registry**

