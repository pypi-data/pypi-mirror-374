from __future__ import annotations

from typing import Any, ClassVar

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ContentOptionsConfigOption(AbstractConfigOption):
    """Holds a list of content-level operations to apply to a file's textual content.

    Example config:
        { "content_options": ["lines_sort", "lines_unique"] }
    """

    OPTION_NAME_LINES_SORT: ClassVar[str] = "lines_sort"
    OPTION_NAME_LINES_UNIQUE: ClassVar[str] = "lines_unique"

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return list[str]
