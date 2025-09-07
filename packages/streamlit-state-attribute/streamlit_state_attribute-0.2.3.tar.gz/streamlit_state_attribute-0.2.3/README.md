# Streamlit State Attribute

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Idea](#idea)
- [Advantages](#advantages)
- [Install](#install)
- [Examples](#examples)
- [Background](#background)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Idea
Instead of using `st.session_state["some_key"]`, define a typed attribute of some class which is automatically synced
with the session state.

```python
from streamlit_state_attribute import StateAttribute
import streamlit as st

class SomeWidget:
    some_attribute: str = StateAttribute(default="test")

some_widget = SomeWidget()
some_widget.some_attribute = "3"
assert st.session_state["SomeWidget.some_attribute"] == "3"
```

## Advantages
 * Handling `st.session_state` is abstracted away
 * Autosuggestions + type hints
 * Logging each state change (default logging level = debug, can be configured per-attribute)
 * Easily build Widgets with their own local state

## Install
```bash
uv pip install streamlit-state-attribute
```

## Examples
```python
import streamlit as st
from streamlit_state_attribute import StateAttribute

class SomeWidgetWithKey:
    key: str
    some_attribute: str = StateAttribute(default="test", unique_attribute="key")

    def __init__(self, key: str) -> None:
        self.key = key


# Each key will have a separate State
other_widget = SomeWidgetWithKey(key="test")
other_widget.some_attribute = "4"
assert st.session_state["SomeWidgetWithKey.test.some_attribute"] == "4"
```
See also [counter.py](src/examples/counter.py) and [global_state.py](src/examples/counter.py).

## Background
Made to play around with [descriptors](https://docs.python.org/3/howto/descriptor.html) after a [workshop descriptors
at Pycon2025](https://pretalx.com/pyconde-pydata-2025/talk/WJPEQH/).
