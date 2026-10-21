

# Switch

A control that allows the user to toggle between checked and not checked.

## Installation 
Copy the following code into your app directory.


> **Error: 'switch' not found in registry**


## Usage


> **Error: 'switch' not found in registry**



## Anatomy
Use the following composition to build a `Switch` component.


```python
switch.root(
    switch.thumb(),
)
```


## Examples

## Description

A standard switch layout featuring a secondary descriptive text block nested alongside the core `field.label` and `switch.root` within a vertical `field.root` layout.


> **Error: 'switch_description' not found in registry**


## Choice Card

Card-style selection where `field.label` wraps the entire `field.root` layout pattern to create a fully clickable target container.


> **Error: 'switch_choice_card' not found in registry**


## Disabled

Pass the `disabled=True` prop directly to the `switch.root` component to deactivate user input. Pass the `data_disabled="true"` attribute to the `field.root` layout component for contextual styling.


> **Error: 'switch_disabled' not found in registry**


## Invalid

Pass the `aria_invalid="true"` prop to the `switch.root` component to explicitly communicate an unfulfilled state. Pass the `data_invalid="true"` attribute to the `field.root` container layout to trigger error typography theme changes automatically.


> **Error: 'switch_invalid' not found in registry**


## Size

Use the `size` property on `switch.root` to scale the toggle boundaries down to `"sm"` or return to `"default"`. Stack components smoothly inside a unified layout using a `field.group` block.


> **Error: 'switch_sizes' not found in registry**

