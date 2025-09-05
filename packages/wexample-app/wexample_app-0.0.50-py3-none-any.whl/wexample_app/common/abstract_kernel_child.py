from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel


class AbstractKernelChild:
    _kernel: AbstractKernel | None

    def __init__(self, kernel: AbstractKernel) -> None:
        from wexample_app.common.abstract_kernel import AbstractKernel

        assert isinstance(kernel, AbstractKernel)

        self._kernel = kernel

    @property
    def kernel(self) -> None:
        return self._kernel

    @kernel.setter
    def kernel(self, value: AbstractKernel) -> None:
        self._kernel = value
