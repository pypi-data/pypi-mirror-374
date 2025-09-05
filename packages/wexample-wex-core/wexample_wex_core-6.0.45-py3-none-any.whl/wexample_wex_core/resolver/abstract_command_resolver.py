from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from wexample_app.resolver.abstract_command_resolver import (
    AbstractCommandResolver as BaseAbstractCommandResolver,
)
from wexample_helpers.const.types import Kwargs, StructuredData

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
    from wexample_wex_core.context.execution_context import ExecutionContext
    from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class AbstractCommandResolver(BaseAbstractCommandResolver, ABC):
    @abstractmethod
    def build_registry_data(self) -> StructuredData:
        pass

    def build_execution_context(
        self,
        middleware: AbstractMiddleware | None,
        command_wrapper: CommandMethodWrapper,
        request: CommandRequest,
        function_kwargs: Kwargs,
    ) -> ExecutionContext:
        from wexample_wex_core.context.execution_context import ExecutionContext

        return ExecutionContext(
            middleware=middleware,
            command_wrapper=command_wrapper,
            request=request,
            function_kwargs=function_kwargs,
        )
