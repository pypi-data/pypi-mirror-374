from __future__ import annotations

from dataclasses import field

from pydantic import BaseModel
from wexample_helpers.const.types import AnyCallable, Kwargs
from wexample_wex_core.command.option import Option
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class CommandMethodWrapper(BaseModel):
    function: AnyCallable
    description: str | None = None
    options: list[Option] = field(default_factory=list)
    middlewares: list[AbstractMiddleware] = field(default_factory=list)
    middlewares_attributes: dict[str, Kwargs] = field(default_factory=dict)

    def set_option(self, option: Option) -> None:
        self.options.append(option)

    def register_middleware(self, name: str, middleware_kwargs: Kwargs) -> None:
        self.middlewares_attributes[name] = middleware_kwargs

    def set_middleware(self, middleware: AbstractMiddleware) -> None:
        self.middlewares.append(middleware)

        for option in middleware.normalized_options:
            self.set_option(option)

    def get_options_names(self) -> list[str]:
        options = []
        for option in self.options:
            options.append(option.name)

        return options

    def find_option_by_name(self, name: str) -> Option | None:
        """Find an option by its name."""
        for option in self.options:
            if option.name == name:
                return option
        return None

    def find_option_by_kebab_name(self, kabab_name: str) -> Option | None:
        """Find an option by its name."""
        for option in self.options:
            if option.kebab_name == kabab_name:
                return option
        return None

    def find_option_by_short_name(self, short_name: str) -> Option | None:
        """Find an option by its short name."""
        for option in self.options:
            if option.short_name == short_name:
                return option
        return None
