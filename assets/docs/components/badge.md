

# Badge

Displays a badge or a component that looks like a badge.

## Installation

Copy the following code into your app directory.


> **Error: 'badge' not found in registry**


## Usage


> **Error: 'badge' not found in registry**


## Anatomy 
Use the following composition to build a `Badge` component.


```python
badge()
```


## Examples

## Variants

Use the `variant` prop to change the variant of the badge.


> **Error: 'badge_with_variants' not found in registry**


## With Icons

You can render an icon inside the badge. Use `data-icon="inline-start"` to render the icon on the left and `data-icon="inline-end"` to render the icon on the right.


> **Error: 'badge_with_icon' not found in registry**


## With Spinner

You can render a spinner inside the badge. Remember to add the `data-icon="inline-start"` or `data-icon="inline-end"` prop to the spinner.


> **Error: 'badge_with_spinner' not found in registry**


## Link

You can pass in `rx.el.a` to turn a badge into a link. The `badge` component accepts `*children` so any interactive element can be passed to it. 


> **Error: 'badge_as_link' not found in registry**


## Custom Colors

You can customize the colors of a badge by adding custom classes such as `bg-green-50 dark:bg-green-800` to the `badge` component.


> **Error: 'badge_custom_colors' not found in registry**



## API Reference

## badge

The `badge` component displays a badge or a component that looks like a badge.

| Prop         | Type                                                                          | Default       |
| ------------ | ----------------------------------------------------------------------------- | ------------- | --------------- | ----------- | --------- | ------- | ----------- |
| -----------  | ----------------------------------------------------------------------------- | -----------   |
| `variant`    | `"default" \                                                                  | "secondary" \ | "destructive" \ | "outline" \ | "ghost" \ | "link"` | `"default"` |
| `class_name` | `string`                                                                      | -             |
