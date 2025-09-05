from __future__ import annotations

from collections.abc import Callable
from typing import Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ActiveConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[bool, Callable[..., Any]]

    @staticmethod
    def is_active(value: bool | Callable[..., Any]) -> bool:
        """Probably not the best way to resolve a value __after__ configuration resolution,
        but it is important to allow "active" option to have callback that are not automatically resolved.
        """
        if callable(value):
            return bool(value())

        return value is True
