from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.item.item_source_file import ItemSourceFile
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    pass


class FileChangeExtensionOperation(FileManipulationOperationMixin, AbstractOperation):
    _original_extension: str | None = None

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.NAME

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate.config_option.should_have_extension_config_option import (
            ShouldHaveExtensionConfigOption,
        )

        if (
            self.target.source
            and self.target.is_file()
            and isinstance(option, ShouldHaveExtensionConfigOption)
        ):
            assert isinstance(self.target.source, ItemSourceFile)
            if (
                self.target.source.get_local_file().get_extension()
                != option.get_value().get_str()
            ):
                return True
        return False

    def describe_before(self) -> str:
        from wexample_filestate.config_option.should_have_extension_config_option import (
            ShouldHaveExtensionConfigOption,
        )

        current_ext = (
            self.target.get_source().get_local_file().get_extension()
            if self.target.get_source()
            else None
        )
        expected_ext = self.target.get_option_value(
            ShouldHaveExtensionConfigOption
        ).get_str()
        path = self.target.get_path().name
        if current_ext is None:
            return f"The file '{path}' has no detectable extension but should have '.{expected_ext}'."
        return f"The file '{path}' has extension '.{current_ext}' but should be '.{expected_ext}'. Its extension will be corrected."

    def describe_after(self) -> str:
        from wexample_filestate.config_option.should_have_extension_config_option import (
            ShouldHaveExtensionConfigOption,
        )

        expected_ext = self.target.get_option_value(
            ShouldHaveExtensionConfigOption
        ).get_str()
        path = self.target.get_path().with_suffix("").name
        return f"The file '{path}' now has the expected extension '.{expected_ext}'."

    def description(self) -> str:
        return "Ensure the file extension matches the configured requirement, correcting it when necessary."

    def apply(self) -> None:
        from wexample_filestate.config_option.should_have_extension_config_option import (
            ShouldHaveExtensionConfigOption,
        )

        self._original_extension = self.target.get_path().with_suffix("").name

        self.target.get_local_file().change_extension(
            self.target.get_option_value(ShouldHaveExtensionConfigOption).get_str()
        )

    def undo(self) -> None:
        self.target.get_local_file().change_extension(self._original_extension)

        self._original_extension = None
