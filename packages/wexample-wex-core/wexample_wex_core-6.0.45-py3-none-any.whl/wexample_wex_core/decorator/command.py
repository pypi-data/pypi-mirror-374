from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable


def command(description: str | None = None):
    def decorator(function: AnyCallable) -> CommandMethodWrapper:
        return CommandMethodWrapper(function=function, description=description)

    return decorator
