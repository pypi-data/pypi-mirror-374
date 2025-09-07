"""Stateful class attributes backed by Streamlit session state.

This package provides the `StateAttribute` descriptor, which lets you define
class attributes that are automatically synchronized with `st.session_state`.
It allows you to model stateful objects in a natural, Pythonic way, while
leveraging Streamlit's built-in persistence between reruns.

Features:
    * Transparent binding of attributes to `st.session_state`.
    * Support for default values or lazily computed defaults via factories.
    * Configurable rerun behavior on assignment or value changes.
    * Log all changes of attributes

Typical use case is when building reusable stateful components in Streamlit
apps—such as widgets, controllers, or domain models—that need consistent state
across reruns without manually managing session keys.

Example:
    >>> import streamlit as st
    >>> from streamlit_state_attribute import StateAttribute
    >>> class Counter:
    ...     value: int = StateAttribute(default=0, rerun="on_change")
    ...
    >>> counter = Counter()
    >>> st.write("Current value:", counter.value)
    >>> if st.button("Increment"):
    ...     counter.value += 1
"""

from .state_attribute import StateAttribute

__all__ = ["StateAttribute"]
