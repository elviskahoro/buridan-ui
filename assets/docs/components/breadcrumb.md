

# Breadcrumb

Displays the path to the current resource using a hierarchy of links.

## Installation

Copy the following code into your app directory.


> **Error: 'breadcrumb' not found in registry**



## Anatomy 
Use the following composition to build a `Breadcrumb` component.


```python
breadcrumb.root(
    breadcrumb.list(
        breadcrumb.item(
            breadcrumb.link(),
        ),
        breadcrumb.separator(),
        breadcrumb.item(
            breadcrumb.page(),
        ),
    ),
)
```


## Examples

## Basic 
A basic breadcrumb with a home link and a components link.


> **Error: 'breadcrumb_basic' not found in registry**


## Custom Separator
Use a custom component as `children` for `breadcrumb.separator` to create a custom separator.


> **Error: 'breadcrumb_custom_separator' not found in registry**


## Dropdown

You can compose `breadcrumb.item` with a `menu.root` to create a dropdown in the breadcrumb.


> **Error: 'breadcrumb_dropdown_demo' not found in registry**


## Collapsed 

We provide a `breadcrumb.ellipsis` component to show a collapsed state when the breadcrumb is too long.


> **Error: 'breadcrumb_ellipsis' not found in registry**


## API Reference

## breadcrumb.root

The `breadcrumb.root` component is the root navigation element that wraps all breadcrumb components.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## breadcrumb.list

The `breadcrumb.list` component displays the ordered list of breadcrumb items.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## breadcrumb.item

The `breadcrumb.item` component wraps individual breadcrumb items.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## breadcrumb.link

The `breadcrumb.link` component displays a clickable link in the breadcrumb.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## breadcrumb.page

The `breadcrumb.page` component displays the current page in the breadcrumb (non-clickable).

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## breadcrumb.separator

The `breadcrumb.separator` component displays a separator between breadcrumb items. You can pass custom children to override the default separator icon.

| Prop         | Type              | Default |
| ------------ | ----------------- | ------- |
| -----------  | ----------------- | ------- |
| `children`   | `rx.Component`    | -       |
| `class_name` | `string`          | -       |

## breadcrumb.ellipsis

The `breadcrumb.ellipsis` component displays an ellipsis indicator for collapsed breadcrumb items.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |
