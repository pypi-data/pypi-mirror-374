from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import PrivateAttr
from wexample_filestate.file_state_manager import FileStateManager

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.common.command_request import CommandRequest
    from wexample_app.const.types import CommandLineArgumentsList


class CommandLineKernel:
    _sys_argv: list[str] = PrivateAttr(default_factory=list)
    _sys_argv_start_index: int = 1
    _sys_argv_end_index: int | None = None
    _core_argv: list[str] = PrivateAttr(default_factory=list)
    _call_workdir: FileStateManager = PrivateAttr()

    def _init_command_line_kernel(self: AbstractKernel) -> None:
        import os
        import sys

        self._sys_argv = sys.argv.copy()
        self._call_workdir = FileStateManager.create_from_path(
            path=os.getcwd(), config={}, io=self.io
        )

        self._handle_core_args()

    def _get_core_args(self: AbstractKernel) -> list[dict[str, Any]]:
        return []

    def _handle_core_args(self: AbstractKernel) -> None:
        from wexample_helpers.helpers.args import args_shift_one

        for arg_config in self._get_core_args():
            if args_shift_one(self._sys_argv, arg_config["arg"], True) is not None:
                setattr(self, f"_config_arg_{arg_config['attr']}", arg_config["value"])

    def _build_command_requests_from_arguments(
        self: AbstractKernel, arguments: CommandLineArgumentsList
    ) -> list[CommandRequest]:
        # By default, allow one request per execution call.
        return self._build_single_command_request_from_arguments(arguments)

    def _build_single_command_request_from_arguments(
        self: AbstractKernel, arguments: CommandLineArgumentsList
    ):
        return [
            self._get_command_request_class()(
                kernel=self, name=arguments[0], arguments=arguments[1:]
            )
        ]

    @property
    def call_workdir(self) -> FileStateManager:
        # Getter is non-optional and always returns a conformant type
        return self._call_workdir

    def exec_argv(self: AbstractKernel) -> None:
        """
        Main entrypoint from command line calls.
        May not be called by an internal script.
        """
        try:
            command_requests = self._build_command_requests_from_arguments(
                self._sys_argv[self._sys_argv_start_index : self._sys_argv_end_index]
            )
        except Exception as e:
            self.io.error(exception=e, fatal=True)

            return

        for command_request in command_requests:
            self.execute_kernel_command_and_print(command_request)
