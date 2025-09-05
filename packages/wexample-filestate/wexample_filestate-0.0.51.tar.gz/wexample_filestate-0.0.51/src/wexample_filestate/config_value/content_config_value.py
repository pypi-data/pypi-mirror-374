from __future__ import annotations

from typing import Any

from wexample_config.config_value.config_value import ConfigValue


class ContentConfigValue(ConfigValue):
    def _create_default_raw(self, raw: Any) -> str:
        return ""

    def build_content(self) -> str | None:
        return self.get_str_or_none()
