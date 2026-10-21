

# Avatar

Displays a user's profile picture, initials, or fallback icon.

## Installation

Copy the following code into your app directory.


> **Error: 'avatar' not found in registry**


## Usage


> **Error: 'avatar' not found in registry**


## Anatomy 
Use the following composition to build an `Avatar` component.


```python
avatar.root(
    avatar.image(),
    avatar.fallback(),
)
```


## Examples

## Basic

A basic avatar component with an image and a fallback.


> **Error: 'avatar_basic' not found in registry**


## Badge

Use the `avatar.badge` component to add a badge to the avatar. The badge is positioned at the bottom right of the avatar.


> **Error: 'avatar_with_badge' not found in registry**


Use the `class_Name` prop to add custom styles to the badge such as custom colors, sizes, etc.

```reflex
avatar.badge(class_name="bg-green-600 dark:bg-green-800")
```

## Badge with Icon

You can also use an icon inside `avatar.badge`.


> **Error: 'avatar_badge_icon' not found in registry**


## Avatar Group

Use the `avatar.group` component to add a group of avatars.


> **Error: 'avatar_as_group' not found in registry**


## Avatar Group Count

Use `avatar.group_count` to add a count to the group.


> **Error: 'avatar_with_group_count' not found in registry**


## Avatar Group with Icon

You can also use an icon inside `avatar.group_count`.


> **Error: 'avatar_group_count_icon' not found in registry**


## Sizes

Use the `size` prop to change the size of the avatar.


> **Error: 'avatar_sizes' not found in registry**


## Dropdown

You can use the `Avatar` component as a trigger for a dropdown menu.


> **Error: 'avatar_dropdown_menu' not found in registry**


## API Reference

## avatar.root

The `avatar.root` component is the root component that wraps the avatar image and fallback.

| Prop         | Type                        | Default     |
| ------------ | --------------------------- | ----------- | ----- | ----------- |
| -----------  | --------------------------- | ----------- |
| `size`       | `"default" \                | "sm" \      | "lg"` | `"default"` |
| `class_name` | `string`                    | -           |

## avatar.image

The `avatar.image` component displays the avatar image. It accepts all Base UI Avatar Image props.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `src`        | `string` | -       |
| `alt`        | `string` | -       |
| `class_name` | `string` | -       |

## avatar.fallback

The `avatar.fallback` component displays a fallback when the image fails to load. It accepts all Base UI Avatar Fallback props.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## avatar.badge

The `avatar.badge` component displays a badge indicator on the avatar, typically positioned at the bottom right.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## avatar.group

The `avatar.group` component displays a group of avatars with overlapping styling.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |

## avatar.group_count

The `avatar.group_count` component displays a count indicator in an avatar group, typically showing the number of additional avatars.

| Prop         | Type     | Default |
| ------------ | -------- | ------- |
| -----------  | -------- | ------- |
| `class_name` | `string` | -       |
