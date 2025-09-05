from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.config_option.text_filter_config_option import (
    TextFilterConfigOption,
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


class ContentEnsureNewlineOperation(FileManipulationOperationMixin, AbstractOperation):
    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.NAME

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate.operation.file_create_operation import (
            FileCreateOperation,
        )

        return [FileCreateOperation]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        if (
            self.target.is_file()
            and self.target.get_local_file().path.exists()
            and isinstance(option, TextFilterConfigOption)
        ):
            value = option.get_value()
            if value is None:
                return False

            # Support both list form ["ensure_newline"] and dict form {"ensure_newline": true}
            has_flag = value.has_item_in_list(
                TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE
            ) or value.has_key_in_dict(
                TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE
            )
            if not has_flag:
                return False

            content = self.target.get_local_file().read()
            return not content.endswith("\n")

        return False

    def description(self) -> str:
        return "Ensure the file content ends with a newline."

    def describe_before(self) -> str:
        return "The file does not end with a newline; one will be added."

    def describe_after(self) -> str:
        return "A trailing newline has been ensured at the end of the file."

    def apply(self) -> None:
        current = self.target.get_local_file().read()
        if not current.endswith("\n"):
            self._target_file_write(content=current + "\n")

    def undo(self) -> None:
        self._restore_target_file()
