

# Accordion

A set of collapsible panels with headings.

## Installation

Copy the following code into your app directory.


> **Error: 'accordion' not found in registry**


## Usage


> **Error: 'accordion' not found in registry**


## Anatomy 
Use the following composition to build an `Accordion` component.


```python
accordion.root(
    accordion.item(
        accordion.header(
            accordion.trigger(),
        ),
        accordion.panel(),
    ),
    accordion.item(
        accordion.header(
            accordion.trigger(),
        ),
        accordion.panel(),
    ),
)
```


## Examples

## Basic

A basic accordion that shows one item at a time. The first item is open by default.


> **Error: 'accordion_basic' not found in registry**


## Multiple

Use the `multiple` prop to allow multiple items to be open at the same time.


> **Error: 'accordion_multiple' not found in registry**


## Disabled

Use the `disabled` prop on `accordion.item` to disable individual items.


> **Error: 'accordion_disabled' not found in registry**


## Borders

Add `border` to the `accordion.root` and `border-b last:border-b-0` to the `accordion.item` to add borders to the items.


> **Error: 'accordion_borders' not found in registry**


## Card

Wrap the `accordion.root` in a `card` component.


> **Error: 'accordion_card' not found in registry**

