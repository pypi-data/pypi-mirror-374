from __future__ import annotations

from typing import Any

from wexample_filestate.workdir.mixin.with_version_workdir_mixin import (
    WithVersionWorkdirMixin,
)
from wexample_helpers.helpers.string import string_ensure_end_with_new_line


class WithAppVersionWorkdirMixin(WithVersionWorkdirMixin):
    def _get_version_default_content(self) -> Any:
        from wexample_filestate.config_value.content_config_value import (
            ContentConfigValue,
        )
        from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

        class VersionBuilder(ContentConfigValue):
            workdir: ProjectWorkdir

            def build_content(self, type_check: bool = True) -> str:
                return string_ensure_end_with_new_line(
                    self.workdir.get_config()
                    .search(path="general.version", default=self.raw)
                    .get_str()
                )

        return VersionBuilder(raw=super()._get_version_default_content(), workdir=self)
