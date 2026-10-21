

# Button

Displays a button or a component that looks like a button.

## Installation

Copy the following code into your app directory.


> **Error: 'button' not found in registry**


## Usage


> **Error: 'button' not found in registry**


## Anatomy 
Use the following composition to build a `Button` component.


```python
button()
```


## Examples

## Sizes

Use the `size` prop to change the size of the button.


> **Error: 'button_size' not found in registry**


## Default


> **Error: 'button_default' not found in registry**


## Secondary


> **Error: 'button_secondary' not found in registry**


## Outline


> **Error: 'button_outline' not found in registry**


## Ghost


> **Error: 'button_ghost' not found in registry**


## Link


> **Error: 'button_link' not found in registry**


## Destructive


> **Error: 'button_destructive' not found in registry**


## Icon


> **Error: 'button_icon' not found in registry**


## With Icon

Remember to add the `data-icon="inline-start"` or `data-icon="inline-end"` attribute to the icon for the correct spacing.


> **Error: 'button_with_icon' not found in registry**


## Rounded

Use the `rounded-full` class to make the button rounded.


> **Error: 'button_rounded' not found in registry**


## Spinner

Render a `spinner()` component inside the button to show a loading state. Remember to add the `data-icon="inline-start"` or `data-icon="inline-end"` attribute to the spinner for the correct spacing.


> **Error: 'button_loading' not found in registry**


## As Link

You can use the `button_variants` helper function to make a link look like a button.

Do **not** use `button(rx.el.a(...))` for links. The Base UI `Button` component always applies `role="button"`, which overrides the semantic link role on `<a>` elements. Use `button_variants` with a plain `rx.el.a` tag instead to cleanly generate the necessary classes as a dynamic Reflex `Var`.


> **Error: 'button_render' not found in registry**



## API Reference

### button()

The `Button` component is a wrapper around the `button` element that adds a variety of styles and functionality.

| Prop      | Type                                                                                 | Default     |
| --------- | ------------------------------------------------------------------------------------ | ----------- | --------- | --------------- | ------------- | ----------- | ----------- | ---------- | ----------- |
| --------- | ------------------------------------------------------------------------------------ | ----------- |
| `variant` | `"default" \                                                                         | "outline" \ | "ghost" \ | "destructive" \ | "secondary" \ | "link"`     | `"default"` |
| `size`    | `"default" \                                                                         | "xs" \      | "sm" \    | "lg" \          | "icon" \      | "icon-xs" \ | "icon-sm" \ | "icon-lg"` | `"default"` |
