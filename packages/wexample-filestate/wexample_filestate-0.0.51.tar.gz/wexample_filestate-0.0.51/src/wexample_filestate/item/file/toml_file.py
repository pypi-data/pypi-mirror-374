from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from wexample_filestate.item.file.structured_content_file import StructuredContentFile

if TYPE_CHECKING:
    from tomlkit import TOMLDocument


class TomlFile(StructuredContentFile):
    EXTENSION_TOML: ClassVar[str] = "toml"

    def _expected_file_name_extension(self) -> str:
        return self.EXTENSION_TOML

    # ---------- Parsing / Serialization ----------
    def loads(self, text: str, strict: bool = False) -> TOMLDocument:  # type: ignore[name-defined]
        # Use tomlkit to preserve comments and formatting during round-trip
        from tomlkit import document, parse

        try:
            if text is None or text == "":
                # Return an empty TOMLDocument to keep types consistent
                return document()
            return parse(text)
        except Exception as e:
            if strict:
                raise e
            # On parse error, return an empty TOMLDocument instead of a dict
            return document()

    def dumps(self, content: TOMLDocument | dict | None) -> str:  # type: ignore[name-defined]
        from tomlkit import document
        from tomlkit import dumps as toml_dumps

        if content is None:
            return toml_dumps(document())

        # If it's already a TOMLDocument, dump as-is to preserve formatting
        try:
            from tomlkit import TOMLDocument as _TOMLDocument

            if isinstance(content, _TOMLDocument):
                return toml_dumps(content)
        except Exception:
            pass

        # Otherwise, attempt to create a TOMLDocument from a dict-like value
        if isinstance(content, dict):
            doc = document()
            for k, v in content.items():
                doc[k] = v
            return toml_dumps(doc)

        # Fallback: stringify
        return str(content)
