from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.item.abstract_item_target import AbstractItemTarget
from wexample_filestate.item.mixins.item_file_mixin import ItemFileMixin


class ItemTargetFile(ItemFileMixin, AbstractItemTarget):
    config: DictConfig | None = None

    def __init__(self, **data) -> None:
        ItemFileMixin.__init__(self, **data)
        AbstractItemTarget.__init__(self, **data)
