from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def option(
    name: str,
    type: type,
    short_name: str | None = None,
    description: str | None = None,
    required: bool = False,
    default: Any = None,
    is_flag: bool = False,
) -> AnyCallable:
    def decorator(command_wrapper: CommandMethodWrapper) -> CommandMethodWrapper:
        from wexample_wex_core.command.option import Option

        command_wrapper.set_option(
            Option(
                name=name,
                short_name=short_name,
                type=type,
                description=description,
                required=required,
                default=default,
                is_flag=is_flag,
            )
        )

        return command_wrapper

    return decorator
