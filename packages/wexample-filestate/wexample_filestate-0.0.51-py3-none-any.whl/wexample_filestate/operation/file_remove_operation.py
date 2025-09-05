from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class FileRemoveOperation(FileManipulationOperationMixin, AbstractOperation):

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.LOCATION

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        return self.target.source and not self.option_should_exist_is_true(self.target)

    def describe_before(self) -> str:
        path = self.target.get_path().as_posix()
        kind = "directory" if self.target.is_directory() else "file"
        return f"The {kind} '{path}' exists but is configured to be absent. It will be removed."

    def describe_after(self) -> str:
        path = self.target.get_path().as_posix()
        return f"'{path}' has been removed as requested by configuration."

    def description(self) -> str:
        return "Remove a file or directory that should not exist according to configuration."

    def apply(self) -> None:
        self._backup_target_file()

        if self.target.is_file():
            os.remove(self._original_path_str)
        elif self.target.is_directory():
            shutil.rmtree(self._original_path_str)

    def undo(self) -> None:
        self._restore_target_file()
