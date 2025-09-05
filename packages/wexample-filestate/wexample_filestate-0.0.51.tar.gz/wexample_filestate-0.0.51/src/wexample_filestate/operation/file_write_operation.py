from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.config_option.content_config_option import ContentConfigOption
from wexample_filestate.config_option.should_contain_lines_config_option import (
    ShouldContainLinesConfigOption,
)
from wexample_filestate.config_option.should_not_contain_lines_config_option import (
    ShouldNotContainLinesConfigOption,
)
from wexample_filestate.operation.abstract_existing_file_operation import (
    AbstractExistingFileOperation,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class FileWriteOperation(AbstractExistingFileOperation):
    @classmethod
    def _apply_on_empty_content(cls) -> bool:
        return True

    @classmethod
    def preview_source_change(cls, target: TargetFileOrDirectoryType) -> str | None:
        from wexample_filestate.config_value.content_config_value import (
            ContentConfigValue,
        )

        """Compute the prospective new content for the target file.

        Returns the updated content string if a change is needed, otherwise None.
        """
        # Start from current content ("" if file does not exist)
        current = cls._read_current_src(target) or ""

        updated_content: str | None = None

        # Exact content override
        content_option = target.get_option_value(ContentConfigOption)
        if content_option and not content_option.is_none():
            assert isinstance(content_option, ContentConfigValue)
            built_content = content_option.build_content()
            if built_content is not None:
                updated_content = built_content

        # Compare the original file content to the overridden version,
        # if target class is producing some content changes.
        class_level_changed_content = target.preview_write(content=updated_content)
        if updated_content != class_level_changed_content:
            updated_content = class_level_changed_content

        # Ensure required lines are present
        should_contain_lines_option = target.get_option_value(
            ShouldContainLinesConfigOption
        )
        if should_contain_lines_option and not should_contain_lines_option.is_none():
            from wexample_helpers.helpers.string import string_append_missing_lines

            base = current if updated_content is None else updated_content
            updated_content = string_append_missing_lines(
                lines=should_contain_lines_option.get_list(),
                content=base,
            )

        # Remove forbidden lines if present
        should_not_contain_lines_option = target.get_option_value(
            ShouldNotContainLinesConfigOption
        )
        if (
            should_not_contain_lines_option
            and not should_not_contain_lines_option.is_none()
        ):
            base = current if updated_content is None else updated_content
            forbidden = set(should_not_contain_lines_option.get_list())
            lines = base.splitlines()
            kept_lines = [l for l in lines if l not in forbidden]
            updated_content = cls._join_with_original_newline(kept_lines, base)
        # If nothing produced, no change.
        if updated_content is None:
            return None

        # If produced content equals current content, no change.
        return updated_content if updated_content != current else None

    @staticmethod
    def _get_current_content_from_target(target: TargetFileOrDirectoryType) -> str:
        src = AbstractExistingFileOperation._read_current_src(target)
        return src if isinstance(src, str) else ""

    @staticmethod
    def _get_current_lines_from_target(
        target: TargetFileOrDirectoryType,
    ) -> list[str]:
        return FileWriteOperation._get_current_content_from_target(target).splitlines()

    @staticmethod
    def _join_with_original_newline(lines: list[str], original: str) -> str:
        """Join lines using \n and preserve a trailing newline if present in original."""
        trailing_newline = original.endswith("\n")
        updated = "\n".join(lines)
        if trailing_newline and (updated or original.splitlines()):
            updated += "\n"
        return updated

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        return self.source_need_change(self.target)

    def describe_before(self) -> str:
        content_option = self.target.get_option(ContentConfigOption)
        should_contain_lines_option = self.target.get_option(
            ShouldContainLinesConfigOption
        )
        should_not_contain_lines_option = self.target.get_option(
            ShouldNotContainLinesConfigOption
        )

        if content_option is not None:
            return "The file content does not match the configured content and will be rewritten."

        if should_contain_lines_option is not None:
            current_lines = self._get_current_lines_from_target(self.target)
            required_lines = self.target.get_option_value(
                ShouldContainLinesConfigOption
            ).get_list()
            missing = [l for l in required_lines if l not in current_lines]
            if missing:
                return f"The file is missing required lines which will be appended: {missing}."
            return "The file already contains all required lines."

        if should_not_contain_lines_option is not None:
            current_lines = self._get_current_lines_from_target(self.target)
            forbidden_lines = self.target.get_option_value(
                ShouldNotContainLinesConfigOption
            ).get_list()
            present = [l for l in forbidden_lines if l in current_lines]
            if present:
                return f"The file contains forbidden lines which will be removed: {present}."
            return "The file does not contain any forbidden lines."

        return "The file content may need to be regenerated based on configuration."

    def describe_after(self) -> str:
        if self.target.get_option(ContentConfigOption) is not None:
            return "The file content has been rewritten to exactly match the configured content."

        if self.target.get_option(ShouldContainLinesConfigOption) is not None:
            return "All required lines are now present in the file."

        if self.target.get_option(ShouldNotContainLinesConfigOption) is not None:
            return "All forbidden lines have been removed from the file."

        return "The file content has been updated according to configuration."

    def description(self) -> str:
        return (
            "Write or update file content to comply with configured content, enforce required lines, "
            "and remove forbidden lines."
        )
