from __future__ import annotations

from typing import ClassVar

from wexample_filestate.item.file.structured_content_file import StructuredContentFile
from wexample_helpers.const.types import JsonContent, StructuredData


class JsonFile(StructuredContentFile):
    EXTENSION_JSON: ClassVar[str] = "json"

    def _expected_file_name_extension(self) -> str:
        return self.EXTENSION_JSON

    # ---------- Parsing / Serialization ----------
    def loads(self, text: str, strict: bool = False) -> JsonContent:  # type: ignore[name-defined]
        import json

        try:
            return json.loads(text)
        except Exception as e:
            if strict:
                raise e
            return {}

    def dumps(self, content: StructuredData | None) -> str:
        import json

        return json.dumps(content or {}, ensure_ascii=False, indent=2)
