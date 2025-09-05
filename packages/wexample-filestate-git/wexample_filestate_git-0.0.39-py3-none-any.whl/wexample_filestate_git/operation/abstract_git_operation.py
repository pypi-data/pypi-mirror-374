from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation

if TYPE_CHECKING:
    from git import Repo
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class AbstractGitOperation(AbstractOperation, ABC):
    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.REMOTE

    # Shared Git helpers
    def _get_target_git_repo(self) -> Repo:
        """Return the GitPython Repo for the target path."""
        from git import Repo

        return Repo(self.target.get_path())

    def _is_active_git_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        if isinstance(option, GitConfigOption):
            value = self.target.get_option_value(GitConfigOption)
            if value:
                if value.has_key_in_dict(ActiveConfigOption.get_name()):
                    active_option = value.get_dict().get(ActiveConfigOption.get_name())
                    return ActiveConfigOption.is_active(active_option)
                return True
        return False

    # Evaluate an 'active' flag consistently across operations.
    # Accepts raw values (bool, int, str, etc.) and treats missing as inactive.
    def _is_active_flag(self, raw_value) -> bool:
        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )

        if raw_value is None:
            return True
        return ActiveConfigOption.is_active(raw_value)
