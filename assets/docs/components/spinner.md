

# Spinner
An indicator that can be used to show a loading state.

> **Note:** The Spinner component is a fully custom implementation using in-line **svg** with no external dependencies.

## Installation 
Copy the following code into your app directory.


> **Error: 'spinner' not found in registry**


## Usage


> **Error: 'spinner' not found in registry**


## Anatomy
Use the following composition to build a `Spinner` component.


```python
spinner()
```


## Examples

## Size
 
Use the `size-*` utility class to change the size of the spinner.
 

> **Error: 'spinner_size' not found in registry**


## Button
 
Add a spinner to a button to indicate a loading state. Place it before the label for a start position.
 

> **Error: 'spinner_button' not found in registry**


## Badge
 
Add a spinner to a badge to indicate a loading or syncing state.
 

> **Error: 'spinner_badge' not found in registry**


## Marker
 
Combine `Spinner` with `Marker` and the `shimmer` utility for animated streaming status indicators. Set `role="status"` so assistive technology announces the update.
 

> **Error: 'spinner_marker' not found in registry**


## API Reference
 
| Prop           | Type     | Default   | Description                                                                     |
| -------------- | -------- | --------- | ------------------------------------------------------------------------------- |
| -------------- | -------- | --------- | --------------------------------------------------                              |
| `class_name`   | `str`    | `""`      | Additional Tailwind classes applied to the icon.                                |
| `**props`      | `dict`   | —         | Any valid HTML attribute forwarded to the element (`role`, `aria_label`, etc.). |
