from __future__ import annotations

from wexample_helpers.exception.not_allowed_item_exception import (
    NotAllowedItemException,
)
from wexample_helpers.exception.undefined_exception import ExceptionData


class CommandUnexpectedArgumentData(ExceptionData):
    """Data model for CommandUnexpectedArgument exception."""

    argument: str


class CommandUnexpectedArgumentException(NotAllowedItemException):
    """Exception raised when an unexpected argument is provided to a command."""

    error_code: str = "COMMAND_UNEXPECTED_ARGUMENT"

    def __init__(
        self,
        argument: str,
        allowed_arguments: list[str],
        cause: Exception | None = None,
        previous: Exception | None = None,
    ) -> None:
        # Call parent constructor with appropriate parameters
        super().__init__(
            item_type="argument",
            item_value=argument,
            allowed_values=allowed_arguments,
            cause=cause,
            previous=previous,
        )
