import logging
from collections.abc import Callable
from typing import Generic, Literal, TypeVar

import streamlit as st

from .unique_attribute_missing_error import UniqueAttributeMissingError

logger = logging.getLogger(__name__)

T = TypeVar("T")
Stateful = TypeVar("Stateful")


class StateAttribute(Generic[T, Stateful]):
    """Descriptor binding attributes to Streamlit's ``st.session_state``.

    Use this class inside your own classes to create attributes that are
    transparently stored in and retrieved from Streamlit's session state.
    This allows you to define stateful models or controllers without
    manually handling session keys.

    Attributes:
        _name: The attribute name as defined on the owner class.
        _owner_cls_name: The name of the class that owns this attribute.
        default: A static default value to use if the key is not yet present.
        default_factory: A callable producing a default value, preferred over
            ``default`` if both are given.
        rerun: Rerun policy for the Streamlit app when the value changes.
            - "never": Do not rerun automatically.
            - "on_change": Rerun only if the new value differs from the old one.
            - "on_assignment": Rerun on every assignment.
        unique_attribute: Optional string used to namespace the key for this
            attribute to avoid collisions across instances.
            This allows you for example to have several Counter classes with different
            values on the same page.
        _log_level: The level at which all state changes should be logged.
    """

    _name: str
    _owner_cls_name: str
    default: T | None
    default_factory: Callable[[], T] | None
    rerun: Literal["never", "on_change", "on_assignment"]
    unique_attribute: str | None
    _log_level: int = logging.DEBUG

    def log(self, msg: str) -> None:
        """Log message with prefix according to `_log_level`."""
        logger.log(level=self._log_level, msg="StateAttribute: " + msg)

    def __init__(
        self,
        default: T | None = None,
        default_factory: Callable[[], T] | None = None,
        rerun: Literal["never", "on_change", "on_assignment"] = "never",
        unique_attribute: str | None = None,
        log_level: int = logging.DEBUG,
    ) -> None:
        self.default = default
        self.default_factory = default_factory
        self.rerun = rerun
        self.unique_attribute = unique_attribute
        self._log_level = log_level

    def __set_name__(self, owner: type[Stateful], name: str) -> None:
        """Set name and owner class name when the attribute is defined in the class."""
        self._name = name
        self._owner_cls_name = owner.__name__

    def session_state_key(self, instance: Stateful) -> str:
        """Return key which is used to get/set value in st.session_state.

        Raises:
            UniqueAttributeMissingError: If unique_attribute is set but not present in class.
        """
        middle = "."
        if self.unique_attribute:
            if not hasattr(instance, self.unique_attribute):
                raise UniqueAttributeMissingError(self, instance)
            middle += getattr(instance, self.unique_attribute) + "."
        return f"{self._owner_cls_name}{middle}{self._name}"

    def __get__(self, instance: Stateful, owner: type[Stateful]) -> T:
        """Get the value either from the streamlit session state or initialize from default.

        Default factory is preferred over default.
        """
        key = self.session_state_key(instance)
        if key in st.session_state:
            return st.session_state[key]
        self.log(f"Key {key} not in session state. Initializing from default...")
        value = (
            self.default_factory() if self.default_factory is not None else self.default
        )
        self.__set__(instance, value)
        return value

    def __set__(self, instance: Stateful, value: T) -> None:
        """Set the value in the streamlit session state (with logging)."""
        key = self.session_state_key(instance)
        prev_value = st.session_state.get(key)
        self.log(
            f"st.session_state[{key!r}]={value!r}   --   (prev. value: {prev_value!r})"
        )
        st.session_state[key] = value
        if self.rerun == "on_assignment" or (
            self.rerun == "on_change" and prev_value != value
        ):
            self.log("Trigger rerun.")
            st.rerun()
