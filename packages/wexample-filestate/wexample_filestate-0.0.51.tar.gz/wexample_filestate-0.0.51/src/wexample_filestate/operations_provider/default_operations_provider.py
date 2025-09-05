from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.operation.content_trim_operation import ContentTrimOperation
from wexample_filestate.operations_provider.abstract_operations_provider import (
    AbstractOperationsProvider,
)

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class DefaultOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> list[type[AbstractOperation]]:
        from wexample_filestate.operation.content_lines_sort_operation import (
            ContentLinesSortOperation,
        )
        from wexample_filestate.operation.content_lines_unique_operation import (
            ContentLinesUniqueOperation,
        )
        from wexample_filestate.operation.file_change_extension_operation import (
            FileChangeExtensionOperation,
        )
        from wexample_filestate.operation.file_create_operation import (
            FileCreateOperation,
        )
        from wexample_filestate.operation.file_remove_operation import (
            FileRemoveOperation,
        )
        from wexample_filestate.operation.file_write_operation import FileWriteOperation
        from wexample_filestate.operation.item_change_mode_operation import (
            ItemChangeModeOperation,
        )
        from wexample_filestate.operation.yaml_sort_recursive_operation import (
            YamlSortRecursiveOperation,
        )

        return [
            ContentLinesSortOperation,
            ContentLinesUniqueOperation,
            ContentTrimOperation,
            FileChangeExtensionOperation,
            FileCreateOperation,
            FileRemoveOperation,
            FileWriteOperation,
            ItemChangeModeOperation,
            YamlSortRecursiveOperation,
        ]
