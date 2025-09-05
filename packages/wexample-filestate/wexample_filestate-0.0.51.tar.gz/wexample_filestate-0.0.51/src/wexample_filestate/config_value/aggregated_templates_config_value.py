from __future__ import annotations

import os
from typing import Any

from wexample_filestate.config_value.content_config_value import ContentConfigValue
from wexample_helpers.const.types import BasicValue
from wexample_helpers.helpers.string import string_replace_params


class AggregatedTemplatesConfigValue(ContentConfigValue):
    raw: Any = None
    templates: list[str] | None = []
    parameters: dict[str, BasicValue] | None = {}

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Any

    def get_templates(self) -> list[str] | None:
        return self.templates

    def build_content(self) -> str | None:
        output = []
        templates = self.get_templates()

        if len(templates) == 0:
            return None
        for template_content in templates:
            output.append(string_replace_params(template_content, self.parameters))

        output_str = os.linesep.join(output)

        return output_str
