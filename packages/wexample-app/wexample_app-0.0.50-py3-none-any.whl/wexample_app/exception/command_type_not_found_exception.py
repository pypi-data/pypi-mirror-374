from __future__ import annotations

from wexample_helpers.exception.undefined_exception import (
    ExceptionData,
    UndefinedException,
)


class CommandTypeNotFoundData(ExceptionData):
    """Data model for CommandTypeNotFound exception."""

    command_name: str


class CommandTypeNotFoundException(UndefinedException):
    """Exception raised when the system cannot determine the type of a command."""

    error_code: str = "COMMAND_TYPE_NOT_FOUND"

    def __init__(
        self,
        command_name: str,
        cause: Exception | None = None,
        previous: Exception | None = None,
    ) -> None:
        # Create structured data using Pydantic model
        data_model = CommandTypeNotFoundData(command_name=command_name)

        # Store command_name as instance attribute for backward compatibility
        self.command_name = command_name

        super().__init__(
            message=f"Unable to determine command type for: {command_name}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous,
        )
