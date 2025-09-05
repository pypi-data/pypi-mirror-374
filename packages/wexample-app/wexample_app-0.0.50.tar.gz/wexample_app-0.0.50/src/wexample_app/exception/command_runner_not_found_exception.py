from __future__ import annotations

from wexample_helpers.exception.undefined_exception import UndefinedException


class CommandRunnerNotFoundException(UndefinedException):
    """Exception raised when no suitable runner is found for a command.

    This exception is thrown when the system cannot find an appropriate runner
    to execute a command, which means the command cannot be executed.
    """

    error_code: str = "COMMAND_RUNNER_NOT_FOUND"

    def __init__(
        self,
        command_name: str,
        cause: Exception | None = None,
        previous: Exception | None = None,
    ) -> None:
        # Store command_name as instance attribute
        self.command_name = command_name

        # Call parent constructor with appropriate parameters
        super().__init__(
            message=f'Not runner found supporting execution of command "{command_name}"',
            cause=cause,
            previous=previous,
        )
