from __future__ import annotations

from wexample_filestate.config_value.aggregated_templates_config_value import (
    AggregatedTemplatesConfigValue,
)


class ReadmeContentConfigValue(AggregatedTemplatesConfigValue):
    def get_templates(self) -> list[str] | None:
        return []
