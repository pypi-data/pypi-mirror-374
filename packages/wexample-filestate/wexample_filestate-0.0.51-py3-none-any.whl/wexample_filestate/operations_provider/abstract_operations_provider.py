from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class AbstractOperationsProvider(BaseModel):
    @staticmethod
    def get_operations() -> list[type[AbstractOperation]]:
        return []
