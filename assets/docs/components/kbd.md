

# Kbd

Used to display textual user input from keyboard.

## Installation

Copy the following code into your app directory.


> **Error: 'kbd' not found in registry**


## Usage


> **Error: 'kbd' not found in registry**


## Anatomy 
Use the following composition to build a `Kbd` component.


```python
kbd.group(
    kbd.root(),
    kbd.root(),
)
```


## Examples

## Group

Use the `kbd.group` component to group keyboard keys together.


> **Error: 'kbd_as_group' not found in registry**


## Button

Use the `kbd.root` component inside a `Button` component to display a keyboard key inside a button.


> **Error: 'kbd_button' not found in registry**


## Tooltip

You can use the `kbd.root` component inside a `Tooltip` component to display a tooltip with a keyboard key.


> **Error: 'kbd_tooltip' not found in registry**


## Input Group

You can use the `kbd.root` component inside a `input_group.addon` component to display a keyboard key inside an input group.


> **Error: 'kbd_input_group' not found in registry**


## API Reference

## kbd.root

Use the `kbd.root` component to display a keyboard key.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | ``      |

```python
kbd.root('Ctrl')
```

## kbd.group

Use the `kbd.group` component to group `kbd.root` components together.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | ``      |

```python
kbd.group(
    kbd.root('Ctrl')
    kbd.root('B')
)
```
