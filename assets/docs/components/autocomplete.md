

# Autocomplete

An input that suggests options as you type.

> **Note:** The Autocomplete is a fully custom component with no external dependencies — built as a self-contained JavaScript component exposed through a Python API for use in Reflex.

## Installation

Copy the following code into your app directory.


> **Error: 'autocomplete' not found in registry**


## Usage


> **Error: 'autocomplete' not found in registry**


## Anatomy 
Use the following composition to build an `Autocomplete` component. 


```python
autocomplete(
    items=[...],
)
```


## Examples

## Basic

A minimal autocomplete with a static list of items.


> **Error: 'autocomplete_basic' not found in registry**


## Selected Value

Wire up `on_select_item` to capture the selected value.


> **Error: 'autocomplete_select_value' not found in registry**


## Grouped List

Pass a `group` key to your data structure to group items together. 


> **Error: 'autocomplete_grouping' not found in registry**


## Large List

Autocomplete works efficiently with large lists — filtering happens entirely in the browser.


> **Error: 'autocomplete_large_list' not found in registry**


## Custom Styling

Override any part of the component by passing a `*_class` prop. Classes are merged with the defaults via `cn`.


> **Error: 'autocomplete_custom_styling' not found in registry**


## Empty State

When no items match the query, the empty state is shown automatically.


> **Error: 'autocomplete_empty_state' not found in registry**


## API Reference

### autocomplete

| Prop                     | Type           | Default | Description                                                                                                                                        |
| ------------------------ | -------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| :---                     | :---           | :---    | :---                                                                                                                                               |
| `items`                  | `list[str]`    | `[]`    | The list of items to display in the dropdown.                                                                                                      |
| `placeholder`            | `str`          | `None`  | Placeholder text shown inside the input when empty.                                                                                                |
| `on_change_query`        | `EventHandler` | `None`  | Fired on every keystroke with the current input value.                                                                                             |
| `on_select_item`         | `EventHandler` | `None`  | Fired when an item is selected, with the selected value as argument.                                                                               |
| `root_class`             | `str`          | `None`  | Additional Tailwind classes merged onto the root wrapper.                                                                                          |
| `input_class`            | `str`          | `None`  | Additional Tailwind classes merged onto the input element.                                                                                         |
| `popup_class`            | `str`          | `None`  | Additional Tailwind classes merged onto the dropdown popup.                                                                                        |
| `list_class`             | `str`          | `None`  | Additional Tailwind classes merged onto the scrollable list.                                                                                       |
| `item_class`             | `str`          | `None`  | Additional Tailwind classes merged onto each list item.                                                                                            |
| `item_highlighted_class` | `str`          | `None`  | Additional Tailwind classes merged onto the currently highlighted item.                                                                            |
| `empty_class`            | `str`          | `None`  | Additional Tailwind classes merged onto the empty state element.                                                                                   |
| `set_query_on_select`    | `bool`         | `True`  | Controls whether selecting an item updates the input value. If `False`, selection clears the input (useful for command palette / navigation mode). |
