from __future__ import annotations

from typing import Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ShouldNotContainLinesConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        # Expect a list of exact line strings to forbid in the file
        return list[str]
