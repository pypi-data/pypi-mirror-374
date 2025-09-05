from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from wexample_config.config_option.abstract_nested_config_option import (
    AbstractNestedConfigOption,
)
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.mixin.item_config_option_mixin import (
    ItemTreeConfigOptionMixin,
)
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.item.mixins.item_mixin import ItemMixin
from wexample_filestate.operations_provider.abstract_operations_provider import (
    AbstractOperationsProvider,
)
from wexample_helpers.const.types import PathOrString
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.mixins.with_io_manager import WithIoManager
from wexample_prompt.mixins.with_io_methods import WithIoMethods

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.const.state_items import SourceFileOrDirectory
    from wexample_filestate.const.types_state_items import (
        SourceFileOrDirectoryType,
        TargetFileOrDirectoryType,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation
    from wexample_filestate.result.abstract_result import AbstractResult
    from wexample_filestate.result.file_state_dry_run_result import (
        FileStateDryRunResult,
    )
    from wexample_filestate.result.file_state_result import FileStateResult
    from wexample_prompt.common.io_manager import IoManager


class AbstractItemTarget(
    WithIoMethods,
    ItemMixin,
    ItemTreeConfigOptionMixin,
    AbstractNestedConfigOption,
    ABC,
):
    source: SourceFileOrDirectory | None = None
    operations_providers: list[type[AbstractOperationsProvider]] | None = None
    last_result: AbstractResult | None = None

    def __init__(
        self,
        io: IoManager | None = None,
        parent_io_handler: WithIoManager | None = None,
        **kwargs,
    ) -> None:
        ItemMixin.__init__(self, **kwargs)
        AbstractNestedConfigOption.__init__(self, **kwargs)
        WithIoMethods.__init__(self, io=io, parent_io_handler=parent_io_handler)

    @classmethod
    def create_from_path(
        cls, path: PathOrString, config: DictConfig | None = None, **kwargs
    ) -> AbstractItemTarget:
        from wexample_helpers.helpers.directory import (
            directory_get_base_name,
            directory_get_parent_path,
        )

        config = config or {}

        manager = cls(base_path=directory_get_parent_path(path), **kwargs)

        config["name"] = (
            config["name"] if config.get("name") else directory_get_base_name(path)
        )
        manager.configure(config=config)
        return manager

    @classmethod
    def create_from_config(cls, **kwargs) -> AbstractItemTarget:
        config = kwargs.get("config")
        instance = cls(**kwargs)
        instance.configure(config)

        return instance

    def configure(self, config: DictConfig) -> None:
        self.set_value(raw_value=config)
        self.locate_source(self.get_path())

    def locate_source(self, path: Path) -> SourceFileOrDirectoryType:
        if path.is_file():
            from wexample_filestate.item.item_source_file import ItemSourceFile

            self.source = ItemSourceFile(
                path=path,
            )
        elif path.is_dir():
            from wexample_filestate.item.item_source_directory import (
                ItemSourceDirectory,
            )

            self.source = ItemSourceDirectory(
                path=path,
            )

        return self.source

    def get_path(self) -> Path:
        # Base path is specified, for instance for the tree root.
        if self.base_path is not None:
            base_path = self.base_path
        else:
            base_path = self.get_parent_item().get_resolved()

        return Path(f"{base_path}{self.get_item_name()}")

    def get_relative_path(self) -> Path | None:
        root = self.get_root()
        if root:
            return self.get_path().relative_to(root.get_path())
        return None

    def get_display_path(self) -> Path:
        return self.get_relative_path() or self.get_path()

    def render_display_path(self) -> str:
        from wexample_helpers.helpers.cli import cli_make_clickable_path

        return cli_make_clickable_path(
            path=self.get_path(),
            short_title=self.get_display_path(),
        )

    def get_operations(self) -> list[type[AbstractOperation]]:
        providers = self.get_operations_providers()
        operations = []

        for provider in providers:
            operations.extend(provider.get_operations())

        return operations

    def get_options_providers(self) -> list[type[AbstractOptionsProvider]]:
        providers = super().get_options_providers()
        if len(providers) > 0:
            return providers

        from wexample_filestate.options_provider.default_options_provider import (
            DefaultOptionsProvider,
        )

        return [
            DefaultOptionsProvider,
        ]

    def build_operations(
        self: TargetFileOrDirectoryType,
        result: AbstractResult,
        scopes: set[Scope] | None = None,
    ) -> None:
        self.io.indentation_up()

        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )
        from wexample_prompt.common.spinner_pool import SpinnerPool

        active_option = self.get_option(ActiveConfigOption)

        # Allow to set active to false
        if not active_option or ActiveConfigOption.is_active(
            active_option.get_value().raw
        ):
            loading_log = self.io.log(
                message=f"{SpinnerPool.next()} {self.get_display_path()}",
            )

            for operation_class in self.get_operations():
                # Instantiate first; we'll test applicability on the instance.
                operation = operation_class(io=self.io, target=self)

                if (
                    scopes is None or operation.get_scope() in scopes
                ) and operation.applicable():
                    self.io.task(
                        f'Applicable operation "{operation_class.get_snake_short_class_name()}" on: {self.get_display_path()}'
                    )
                    result.operations.append(operation)

            if self.io.default_context_verbosity != VerbosityLevel.MAXIMUM:
                self.io.erase_response(loading_log)

        self.io.indentation_down()

    def get_operations_providers(self) -> list[type[AbstractOperationsProvider]]:
        if self.parent:
            return cast(
                AbstractItemTarget, self.get_parent_item()
            ).get_operations_providers()

        if self.operations_providers:
            return self.operations_providers

        from wexample_filestate.operations_provider.default_operations_provider import (
            DefaultOperationsProvider,
        )

        return [
            DefaultOperationsProvider,
        ]

    def get_item_name(self) -> str:
        from wexample_config.config_option.name_config_option import NameConfigOption

        return self.get_option(NameConfigOption).get_value().get_str()

    def get_source(self) -> SourceFileOrDirectory:
        assert self.source is not None
        return self.source

    def dump(self) -> Any:
        output = super().dump()
        output["name"] = self.get_item_name()

        return output

    def rollback(self) -> FileStateResult:
        from wexample_filestate.result.file_state_result import FileStateResult

        result = FileStateResult(state_manager=self, rollback=True)

        # Fetch applied operations to a new stack.
        if self.last_result:
            for operation in self.last_result.operations:
                if operation.applied:
                    result.operations.append(operation)

        result.apply_operations()
        self.last_result = result

        return result

    def dry_run(self, scopes: set[Scope] | None = None) -> FileStateDryRunResult:
        from wexample_filestate.result.file_state_dry_run_result import (
            FileStateDryRunResult,
        )

        result = FileStateDryRunResult(state_manager=self)
        self.last_result = result
        self.build_operations(result=result, scopes=scopes)
        result.apply_operations()

        return result

    def apply(
        self,
        interactive: bool = False,
        scopes: set[Scope] | None = None,
    ) -> FileStateResult:
        from wexample_filestate.result.file_state_result import FileStateResult

        result = FileStateResult(state_manager=self)
        self.last_result = result
        self.build_operations(result=result, scopes=scopes)

        if len(result.operations) > 0:
            result.apply_operations(interactive=interactive)
        else:
            from wexample_helpers.helpers.cli import cli_make_clickable_path

            self.io.info(
                message=f"No operation to execute on: {cli_make_clickable_path(self.get_path())} ",
            )

        return result

    def find_closest(
        self, class_type: type[AbstractItemTarget]
    ) -> AbstractItemTarget | None:
        """Return the nearest parent item that is an instance of class_type.

        Traverses parents via self.get_parent_item_or_none() until a match is found
        or the root is reached.
        """
        current = self.get_parent_item_or_none()
        while current is not None:
            if isinstance(current, class_type):
                return current  # type: ignore[return-value]
            current = current.get_parent_item_or_none()
        return None

    def get_env_parameter(self, key: str, default: str | None = None) -> str | None:
        """If no environment parameter defined by current item, ask its parent.
        The default behavior is to return default value but should be replaced by,
        for instance, .env loading in specific contexts"""
        parent_item = self.get_parent_item_or_none()
        if parent_item:
            return parent_item.get_env_parameter(
                key=key,
                default=default,
            )
        return default
