

# Input Group

Add addons, buttons, and helper content to inputs.

## Installation

Copy the following code into your app directory.


> **Error: 'input_group' not found in registry**


## Usage


> **Error: 'input_group' not found in registry**


## Anatomy 
Use the following composition to build an `Input Group` component.


```python
input_group.root(
    input_group.input(placeholder="Search..."),
    input_group.addon(),
)
```


## Align

Use the `align` prop on `input_group.addon` to position the addon relative to the input.

>For proper focus management, **input_group.addon** should always be placed after **input_group.input** or **input_group.textarea** in the DOM. Use the **align** prop to visually position the addon.


## inline-start

Use `align="inline-start"` to position the addon at the start of the input. This is the default.


> **Error: 'input_group_inline_start' not found in registry**


## inline-end

Use `align="inline-end"` to position the addon at the end of the input.


> **Error: 'input_group_inline_end' not found in registry**


## block-start

Use `align="block-start"` to position the addon above the input.


> **Error: 'input_group_block_start' not found in registry**


## block-end

Use `align="block-end"` to position the addon below the input.


> **Error: 'input_group_block_end' not found in registry**


## Examples

## Icons

> **Error: 'input_group_icons' not found in registry**


## Text

> **Error: 'input_group_text' not found in registry**


## Button

> **Error: 'input_group_button' not found in registry**


## Spinner

> **Error: 'input_group_spinner' not found in registry**


## Dropdown

> **Error: 'input_group_dropdown' not found in registry**


## API Reference

## input_group.root

The main component that wraps inputs and addons.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` |         |


## input_group.addon

Displays icons, text, buttons, or other content alongside inputs.

>For proper focus navigation, the `input_group.addon` component should be placed after the input. Set the `align` prop to position the addon.

| Prop         | Type                                                             | Default          |
| ------------ | ---------------------------------------------------------------- | ---------------- | --------------- | ------------ | ---------------- |
| -----------  | ---------------------------------------------------------------- | ---------------- |
| `align`      | `"inline-start" \                                                | "inline-end" \   | "block-start" \ | "block-end"` | `"inline-start"` |
| `class_name` | `string`                                                         |                  |


>For **input_group.input**, use the **inline-start** or **inline-end** alignment. For **input_group.textarea**, use the **block-start** or **block-end** alignment.

The `input_group.addon` component can have multiple `input_group.button` components and icons.

## input_group.button

Displays buttons within input groups. See the [Button](/docs/components/button) docs for more information. 

| Prop         | Type                                                                          | Default         |
| ------------ | ----------------------------------------------------------------------------- | --------------- | ----------- | ------------- | --------- | ------- | --------- |
| -----------  | ----------------------------------------------------------------------------- | ---------       |
| `size`       | `"xs" \                                                                       | "icon-xs" \     | "sm" \      | "icon-sm"`    | `"xs"`    |
| `variant`    | `"default" \                                                                  | "destructive" \ | "outline" \ | "secondary" \ | "ghost" \ | "link"` | `"ghost"` |
| `class_name` | `string`                                                                      |                 |

## input_group.input

Replacement for `input()` when building input groups. This component has the input group styles pre-applied and uses the unified `data-slot="input-group-control"` for focus state handling.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` |         |

All other props are passed through to the underlying `Input()` component.

## input_group.textarea

Replacement for `textarea()` when building input groups. This component has the textarea group styles pre-applied and uses the unified `data-slot="input-group-control"` for focus state handling.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` |         |

All other props are passed through to the underlying `textarea()` component.
