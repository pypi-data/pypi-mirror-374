from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_filestate.config_option.mode_config_option import ModeConfigOption
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_helpers.helpers.file import (
    file_change_mode,
    file_change_mode_recursive,
    file_mode_octal_to_num,
    file_path_get_mode_num,
    file_validate_mode_octal_or_fail,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class ItemChangeModeOperation(AbstractOperation):
    _original_octal_mode: str | None = None

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.PERMISSIONS

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        if not self.target.source:
            return False

        if isinstance(option, ModeConfigOption):
            file_validate_mode_octal_or_fail(option.get_octal())
            return (
                file_path_get_mode_num(self.target.get_source().get_path())
                != option.get_int()
            )

        return False

    def describe_before(self) -> str:
        from wexample_filestate.config_option.mode_config_option import ModeConfigOption

        current_octal = self.target.get_source().get_octal_mode()
        target_octal = self.target.get_option_value(ModeConfigOption).get_str()
        path = self.target.get_path().as_posix()
        return f"The item '{path}' has permissions {current_octal} but should be {target_octal}. Permissions will be updated."

    def describe_after(self) -> str:
        from wexample_filestate.config_option.mode_config_option import ModeConfigOption

        path = self.target.get_path().as_posix()
        target_octal = self.target.get_option_value(ModeConfigOption).get_str()
        return f"Permissions for '{path}' are now set to {target_octal}."

    def description(self) -> str:
        return "Ensure file or directory permissions match the configured mode."

    def apply(self) -> None:
        from wexample_filestate.config_option.mode_recursive_config_option import (
            ModeRecursiveConfigOption,
        )

        self._original_octal_mode = self.target.get_source().get_octal_mode()
        mode_int = cast(
            ModeConfigOption, self.target.get_option(ModeConfigOption)
        ).get_int()
        mode_recursive_option = self.target.get_option(ModeRecursiveConfigOption)

        if (
            mode_recursive_option
            and mode_recursive_option.get_value().get_bool() is True
        ):
            file_change_mode(self.target.get_source().get_path_str(), mode_int)
        else:
            file_change_mode_recursive(
                self.target.get_source().get_path_str(), mode_int
            )

    def undo(self) -> None:
        file_change_mode_recursive(
            self.target.get_source().get_path_str(),
            file_mode_octal_to_num(self._get_original_octal_mode()),
        )

    def _get_original_octal_mode(self) -> str:
        assert self._original_octal_mode is not None
        return self._original_octal_mode
