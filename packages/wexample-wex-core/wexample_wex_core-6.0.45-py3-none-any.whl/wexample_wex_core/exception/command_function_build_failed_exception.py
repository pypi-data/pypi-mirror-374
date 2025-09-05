from __future__ import annotations

from wexample_helpers.exception.undefined_exception import (
    ExceptionData,
    UndefinedException,
)


class CommandFunctionBuildFailedData(ExceptionData):
    """Data model for CommandFunctionBuildFailed exception."""

    command_name: str
    expected_type: str
    actual_type: str


class CommandFunctionBuildFailedException(UndefinedException):
    """Exception raised when a command function could not be built correctly.

    This exception is thrown when the system tries to build a command function but
    the result is not of the expected type, indicating an issue with the command
    declaration or implementation.
    """

    error_code: str = "COMMAND_FUNCTION_BUILD_FAILED"

    def __init__(
        self,
        command_name: str,
        expected_type: str,
        actual_type: str,
        cause: Exception | None = None,
        previous: Exception | None = None,
    ) -> None:
        # Create structured data using Pydantic model
        data_model = CommandFunctionBuildFailedData(
            command_name=command_name,
            expected_type=expected_type,
            actual_type=actual_type,
        )

        # Store attributes as instance attributes
        self.command_name = command_name
        self.expected_type = expected_type
        self.actual_type = actual_type

        super().__init__(
            message=f"Failed to build command function for '{command_name}'. Expected type '{expected_type}' but got '{actual_type}'.",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous,
        )
