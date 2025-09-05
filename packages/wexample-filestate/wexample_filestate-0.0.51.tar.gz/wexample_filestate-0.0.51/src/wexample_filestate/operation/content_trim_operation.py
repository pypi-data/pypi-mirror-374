from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.config_option.text_filter_config_option import (
    TextFilterConfigOption,
)
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    pass


class ContentTrimOperation(FileManipulationOperationMixin, AbstractOperation):
    _original_extension: str | None = None

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.CONTENT

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate.operation.file_create_operation import (
            FileCreateOperation,
        )

        return [FileCreateOperation]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate.config_option.text_filter_config_option import (
            TextFilterConfigOption,
        )

        if (
            self.target.is_file()
            and self.target.get_local_file().path.exists()
            and isinstance(option, TextFilterConfigOption)
        ):
            value = option.get_value()
            if value is None:
                return False

            # Accept both list form ["trim"] and dict form {"trim": {...}}
            has_trim = value.has_item_in_list(
                TextFilterConfigOption.OPTION_NAME_TRIM
            ) or value.has_key_in_dict(TextFilterConfigOption.OPTION_NAME_TRIM)
            if has_trim:
                content = self.target.get_local_file().read()
                char = option.get_trimmed_char()
                return content.startswith(char) or content.endswith(char)
        return False

    def _get_trimmed_char(self) -> str:
        return self.target.get_option(TextFilterConfigOption).get_trimmed_char()

    def describe_before(self) -> str:
        return f"The file contains a leading or trailing character {repr(self._get_trimmed_char())} that should be trimmed."

    def describe_after(self) -> str:
        return f"The file content has been trimmed to remove the character {repr(self._get_trimmed_char())}."

    def description(self) -> str:
        return "Trim the file content according to the given character."

    def apply(self) -> None:
        self._target_file_write(
            content=self.target.get_local_file().read().strip(self._get_trimmed_char())
        )

    def undo(self) -> None:
        self._restore_target_file()
