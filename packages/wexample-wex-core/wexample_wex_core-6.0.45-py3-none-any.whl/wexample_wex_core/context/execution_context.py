from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, PrivateAttr
from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.classes.mixin.printable_mixin import PrintableMixin
from wexample_helpers.const.types import Kwargs
from wexample_prompt.mixins.with_required_io_manager import WithRequiredIoManager
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper
from wexample_wex_core.common.command_request import CommandRequest
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware

if TYPE_CHECKING:
    from wexample_prompt.common.progress.progress_handle import ProgressHandle


class ExecutionContext(
    AbstractKernelChild,
    WithRequiredIoManager,
    PrintableMixin,
    BaseModel,
):
    command_wrapper: CommandMethodWrapper
    function_kwargs: Kwargs = Field(default_factory=dict)
    middleware: AbstractMiddleware | None
    request: CommandRequest
    _current_progress: ProgressHandle | None = PrivateAttr(default=None)

    def __init__(self, **kwargs) -> None:
        BaseModel.__init__(self, **kwargs)

        AbstractKernelChild.__init__(self, kernel=self.request.kernel)

        WithRequiredIoManager.__init__(self, io=self.kernel.io)

        self.function_kwargs["context"] = self

    def create_progress_range(self, **kwargs) -> ProgressHandle:
        self._current_progress = self.get_or_create_progress().create_range_handle(
            **kwargs
        )
        return self._current_progress

    def get_or_create_progress(self, **kwargs) -> ProgressHandle:
        if self._current_progress is None:
            self._current_progress = self.io.progress(
                **kwargs, context=self.io.create_context()
            ).get_handle()
        return self._current_progress

    def finish_progress(self, **kwargs) -> ProgressHandle:
        self._current_progress.finish()

        self._current_progress = self._current_progress.parent
        self._current_progress.update(**kwargs)
        return self._current_progress
