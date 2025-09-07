from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .state_attribute import StateAttribute


class UniqueAttributeMissingError(AttributeError):
    """StateAttribute has unique_attribute defined which is missing at the parent class."""

    def __init__(self, sa: "StateAttribute", instance: Any) -> None:
        # noinspection PyProtectedMember
        message = f"""
    class {sa._owner_cls_name}:
        ...
        {sa._name} = StateAttribute(..., unique_attribute={sa.unique_attribute!r})
        ...

    The class {sa._owner_cls_name} only has the following attributes: {list(instance.__dict__)}
        """  # noqa: SLF001
        super().__init__(message)
