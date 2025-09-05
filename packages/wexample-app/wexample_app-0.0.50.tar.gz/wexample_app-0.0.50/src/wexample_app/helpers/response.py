from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.response.abstract_response import AbstractResponse


def response_normalize(kernel: AbstractKernel, response: Any) -> AbstractResponse:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_app.response.null_response import NullResponse

    if isinstance(response, AbstractResponse):
        return response
    if isinstance(response, bool):
        from wexample_app.response.boolean_response import BooleanResponse

        return BooleanResponse(kernel=kernel, content=response)
    if response is None:
        return NullResponse(kernel=kernel)

    from wexample_app.response.default_response import DefaultResponse

    return DefaultResponse(kernel=kernel, content=response)
