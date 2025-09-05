from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import PrivateAttr
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.file_state_manager import FileStateManager
from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig
    from wexample_prompt.common.io_manager import IoManager


class WithWorkdirMixin:
    # Private attributes to avoid Pydantic field processing while keeping strong typing
    _workdir: FileStateManager | None = PrivateAttr(default=None)
    _host_workdir: FileStateManager | None = PrivateAttr(default=None)

    @property
    def workdir(self) -> FileStateManager | None:
        return self._workdir

    @workdir.setter
    def workdir(self, value: FileStateManager | None) -> None:
        self._workdir = value

    @property
    def host_workdir(self) -> FileStateManager | None:
        return self._host_workdir

    @host_workdir.setter
    def host_workdir(self, value: FileStateManager | None) -> None:
        self._host_workdir = value

    def _init_workdir(
        self,
        entrypoint_path: str,
        io: IoManager,
        config: DictConfig | None = None,
    ) -> None:
        import os

        self.workdir = self._get_workdir_state_manager_class(
            entrypoint_path=entrypoint_path,
            io=io,
            config=config,
        )

        # Hide core config logs
        original_verbosity = io.default_response_verbosity
        io.default_response_verbosity = VerbosityLevel.MAXIMUM

        # Ensure files state, but not content at this point.
        self.workdir.apply(
            scopes={
                Scope.LOCATION,
                Scope.NAME,
                Scope.OWNERSHIP,
                Scope.PERMISSIONS,
                Scope.TIMESTAMPS,
            },
        )

        io.default_response_verbosity = original_verbosity

        # The calling workdir may be in a virtual env host system.
        self.host_workdir = FileStateManager.create_from_path(path=os.getcwd(), io=io)

    def _rebuild_workdir_content(self) -> None:
        self.workdir.apply(
            scopes={
                Scope.CONTENT,
            }
        )

    def _get_workdir_state_manager_class(
        self,
        entrypoint_path: str,
        io: IoManager,
        config: DictConfig | None = None,
    ) -> FileStateManager:
        return FileStateManager.create_from_path(
            path=entrypoint_path, config=config or {}, io=io
        )
