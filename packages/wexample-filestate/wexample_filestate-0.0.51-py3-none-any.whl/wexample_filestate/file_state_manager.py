from __future__ import annotations

from typing import ClassVar

from wexample_config.const.types import DictConfig
from wexample_filestate.item.item_target_directory import ItemTargetDirectory
from wexample_helpers.classes.mixin.import_packages_mixin import ImportPackagesMixin


class FileStateManager(ImportPackagesMixin, ItemTargetDirectory):
    # Minimal declaration; other mixins/classes can contribute via ImportPackagesMixin
    import_packages: ClassVar[tuple[str, ...]] = (
        "wexample_filestate.const",
        "wexample_filestate.result",
        "wexample_filestate.operation",
    )

    def __init__(self, **data) -> None:
        super().__init__(value=None, **data)

    def configure(self, config: DictConfig) -> None:
        super().configure(config=config)

        # As root
        self.build_item_tree()

    # Lazy bootstrap: ensure imports are loaded once before creating from path
    @classmethod
    def create_from_path(cls, *args, **kwargs):  # type: ignore[override]
        cls.load_imports()
        return super().create_from_path(*args, **kwargs)
