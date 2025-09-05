from __future__ import annotations

from wexample_helpers.exception.undefined_exception import (
    ExceptionData,
    UndefinedException,
)


class CommandFunctionNotFoundData(ExceptionData):
    """Data model for CommandFunctionNotFound exception."""

    function_name: str
    module_path: str


class CommandFunctionNotFoundException(UndefinedException):
    """Exception raised when a command function cannot be found in the module."""

    error_code: str = "COMMAND_FUNCTION_NOT_FOUND"

    def __init__(
        self,
        function_name: str,
        module_path: str,
        cause: Exception | None = None,
        previous: Exception | None = None,
    ) -> None:
        # Create structured data using Pydantic model
        data_model = CommandFunctionNotFoundData(
            function_name=function_name, module_path=module_path
        )

        # Store attributes as instance attributes for backward compatibility
        self.function_name = function_name
        self.module_path = module_path

        super().__init__(
            message=f"Command function '{function_name}' not found in module: {module_path}",
            data=data_model.model_dump(),
            cause=cause,
            previous=previous,
        )
