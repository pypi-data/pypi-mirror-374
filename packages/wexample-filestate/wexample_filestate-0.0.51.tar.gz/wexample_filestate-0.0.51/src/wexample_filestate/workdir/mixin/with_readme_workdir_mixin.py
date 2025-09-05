from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.text_filter_config_option import (
    TextFilterConfigOption,
)
from wexample_filestate.const.disk import DiskItemType

if TYPE_CHECKING:
    from wexample_filestate.config_value.readme_content_config_value import (
        ReadmeContentConfigValue,
    )


class WithReadmeWorkdirMixin:
    README_FILENAME: ClassVar[str] = "README.md"

    def append_readme(self, config: DictConfig | None = None) -> DictConfig:
        from wexample_filestate.config_value.readme_content_config_value import (
            ReadmeContentConfigValue,
        )

        config.get("children").append(
            {
                "name": self.README_FILENAME,
                "type": DiskItemType.FILE,
                "should_exist": True,
                "content": self._get_readme_content(),
                "default_content": ReadmeContentConfigValue(
                    templates=[], parameters={}
                ),
                "text_filter": [TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE],
            }
        )

        return config

    def _get_readme_content(self) -> ReadmeContentConfigValue | None:
        from wexample_filestate.config_value.readme_content_config_value import (
            ReadmeContentConfigValue,
        )

        return ReadmeContentConfigValue()
