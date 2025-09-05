from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    pass


class YamlSortRecursiveOperation(FileManipulationOperationMixin, AbstractOperation):
    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.CONTENT

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate.operation.file_create_operation import (
            FileCreateOperation,
        )

        return [FileCreateOperation]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate.config_option.yaml_filter_config_option import (
            YamlFilterConfigOption,
        )

        if (
            self.target.is_file()
            and self.target.get_local_file().path.exists()
            and isinstance(option, YamlFilterConfigOption)
        ):
            value = option.get_value()
            if value is None:
                return False

            # Only applicable if the flag is set (support list or dict form)
            has_flag = value.has_item_in_list(
                "sort_recursive"
            ) or value.has_key_in_dict("sort_recursive")
            if not has_flag:
                return False

            # read() already returns parsed YAML (dict/list) or None for YAML files
            # Use internal helper to detect if sorting is needed
            return not YamlSortRecursiveOperation._is_sorted(
                data=self.target.get_local_file().read()
            )

        return False

    @staticmethod
    def _is_sorted(data: Any) -> bool:
        """Return True if the current YAML content is already recursively key-sorted."""
        import yaml

        if not isinstance(data, str):
            return True

        try:
            data = yaml.safe_load(data)
        except Exception:
            # Unparseable, consider it not applicable for sorting
            return True

        def sort_rec(obj):
            if isinstance(obj, dict):
                return {k: sort_rec(obj[k]) for k in sorted(obj.keys())}
            if isinstance(obj, list):
                return [sort_rec(v) for v in obj]
            return obj

        sorted_data = sort_rec(data)
        current_dump = yaml.safe_dump(data, sort_keys=False)
        sorted_dump = yaml.safe_dump(sorted_data, sort_keys=False)
        return current_dump == sorted_dump

    def description(self) -> str:
        return "Sort YAML keys recursively in alphabetical order."

    def describe_before(self) -> str:
        return "The YAML file may have unsorted keys; applying recursive alphabetical sort."

    def describe_after(self) -> str:
        return "The YAML file keys have been recursively sorted alphabetically."

    def apply(self) -> None:
        import yaml

        data = self.target.get_local_file().read()
        if isinstance(data, str):
            data = yaml.safe_load(data)

        def sort_rec(obj):
            if isinstance(obj, dict):
                return {k: sort_rec(obj[k]) for k in sorted(obj.keys())}
            if isinstance(obj, list):
                return [sort_rec(v) for v in obj]
            return obj

        sorted_data = sort_rec(data)
        # Preserve a stable YAML dump
        dumped = yaml.safe_dump(sorted_data, sort_keys=False)

        self._target_file_write(content=dumped)

    def undo(self) -> None:
        self._restore_target_file()
