from __future__ import annotations

from typing import ClassVar

from wexample_config.config_value.config_value import ConfigValue
from wexample_filestate.item.file.structured_content_file import StructuredContentFile
from wexample_helpers.const.types import StructuredData
from wexample_helpers_yaml.const.types import YamlContent


class YamlFile(StructuredContentFile):
    EXTENSION_YAML: ClassVar[str] = "yaml"
    EXTENSION_YML: ClassVar[str] = "yml"

    def _expected_file_name_extension(self) -> str:
        return self.EXTENSION_YML

    def loads(self, text: str, strict: bool = False) -> YamlContent:
        import yaml

        try:
            value = yaml.safe_load(text)
            # Normalize None to empty dict for convenience
            return value if value is not None else {}
        except Exception as e:
            if strict:
                raise e
            return {}

    def dumps(self, content: StructuredData | None) -> str:
        import yaml

        # Avoid dumping ConfigValue directly; convert to primitive via str by default
        def _normalize(v):
            if isinstance(v, ConfigValue):
                return str(v)
            if isinstance(v, dict):
                return {k: _normalize(x) for k, x in v.items()}
            if isinstance(v, list):
                return [_normalize(x) for x in v]
            return v

        normalized = _normalize(content or {})
        return yaml.safe_dump(normalized)
