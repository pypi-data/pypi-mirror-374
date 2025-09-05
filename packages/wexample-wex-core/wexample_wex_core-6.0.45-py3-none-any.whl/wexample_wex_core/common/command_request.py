from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.common.command_request import CommandRequest as BaseCommandRequest

if TYPE_CHECKING:
    pass


class CommandRequest(BaseCommandRequest):
    request_id: str

    def get_addon_manager(self):
        return self.resolver.get_request_addon_manager(self)
