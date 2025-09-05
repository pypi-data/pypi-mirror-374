from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.config_option.content_options_config_option import (
    ContentOptionsConfigOption,
)
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class ContentLinesUniqueOperation(FileManipulationOperationMixin, AbstractOperation):
    """Ensure each line of the file content is unique (remove duplicates preserving order).

    Triggered by: { "content_options": ["lines_unique"] }
    """

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.CONTENT

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        if not isinstance(option, ContentOptionsConfigOption):
            return False

        value = option.get_value()
        if value is None or not value.has_item_in_list(
            ContentOptionsConfigOption.OPTION_NAME_LINES_UNIQUE
        ):
            return False

        local_file = self.target.get_local_file()
        if not self.target.is_file() or not local_file.path.exists():
            # If the file doesn't exist, nothing to uniquify yet.
            return False

        src = local_file.read()
        unique_src = self._unique_lines_content(src)
        return unique_src != src

    @staticmethod
    def _unique_lines_content(src: str) -> str:
        # Preserve a trailing newline if it exists
        had_trailing_newline = src.endswith("\n")
        lines = src.splitlines()
        seen: set[str] = set()
        unique_lines: list[str] = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        out = "\n".join(unique_lines)
        if had_trailing_newline:
            out += "\n"
        return out

    def describe_before(self) -> str:
        return "The file contains duplicate lines."

    def describe_after(self) -> str:
        return "All duplicate lines have been removed, preserving original order."

    def description(self) -> str:
        return "Ensure content lines are unique by removing duplicates and preserving order."

    def apply(self) -> None:
        src = self.target.get_local_file().read()
        updated = self._unique_lines_content(src)
        if updated != src:
            self._target_file_write(content=updated)

    def undo(self) -> None:
        self._restore_target_file()
