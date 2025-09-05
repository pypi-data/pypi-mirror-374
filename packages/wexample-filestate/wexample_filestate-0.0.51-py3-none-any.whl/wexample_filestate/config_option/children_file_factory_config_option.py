from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import Field
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.abstract_children_manipulator_config_option import (
    AbstractChildrenManipulationConfigOption,
)
from wexample_filestate.const.disk import DiskItemType

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class ChildrenFileFactoryConfigOption(AbstractChildrenManipulationConfigOption):
    # Pattern is a template used to create generated child configs (e.g., name/type for files to add under each matched directory)
    pattern: DictConfig
    # Whether to recurse into subdirectories when generating children from the base path
    recursive: bool = Field(
        default=False,
        description="Recurse into subdirectories when generating children from matched directories.",
    )

    def _generate_children_recursive(
        self,
        path: Path,
    ) -> DictConfig:
        dir_config = {
            "name": path.name,
            "type": DiskItemType.DIRECTORY,
            "children": [],
            "should_exist": True,
        }

        if self._path_match_patterns(path.name):
            dir_config["children"].append(
                {
                    "name": self.pattern["name"],
                    "type": self.pattern["type"],
                    "should_exist": True,
                }
            )

        if self.recursive:
            # Iterate safely over child entries using Path API
            for entry in path.iterdir():
                if entry.is_dir():
                    dir_config["children"].append(
                        self._generate_children_recursive(
                            path=entry,
                        )
                    )
        return dir_config

    def generate_children(self) -> list[TargetFileOrDirectoryType]:
        self.pattern
        children = []
        path = self.get_parent_item().get_path()

        if path.exists():
            directories = self._get_directories_filtered(base_path=path)

            for directory in directories:
                directory_path = Path(directory)

                dir_config = self._generate_children_recursive(
                    path=directory_path,
                )

                children.append(
                    self._create_children_from_config(
                        path=directory_path,
                        config=dir_config,
                    )
                )

        return children
