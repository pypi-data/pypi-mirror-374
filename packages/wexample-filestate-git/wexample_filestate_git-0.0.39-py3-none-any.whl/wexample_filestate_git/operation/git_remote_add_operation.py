from __future__ import annotations

from typing import TYPE_CHECKING, cast

from git import Repo
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation
from wexample_helpers_git.helpers.git import git_is_init, git_remote_create_once

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class GitRemoteAddOperation(FileManipulationOperationMixin, AbstractGitOperation):
    _original_path_str: str
    _created_remote: dict[str, bool]

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._created_remote = {}

    def dependencies(self) -> list[type[AbstractOperation]]:
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        return [GitInitOperation]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        if not self._is_active_git_option(option):
            return False

        assert isinstance(option, GitConfigOption)
        if option.should_have_git() and git_is_init(self.target.get_path()):
            value = self.target.get_option_value(GitConfigOption)
            if not value or not value.has_key_in_dict("remote"):
                return False

            return self._is_remote_missing_or_mismatched()

    def describe_before(self) -> str:
        desc = self._remotes_description()
        if desc:
            return f"Remote missing in .git directory: {desc}"
        return "Remote missing in .git directory"

    def describe_after(self) -> str:
        desc = self._remotes_description()
        if desc:
            return f"Remote added in .git directory: {desc}"
        return "Remote added in .git directory"

    def description(self) -> str:
        return "Add remote in .git directory"

    def apply(self) -> None:
        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        value = self.target.get_option_value(GitConfigOption)

        if value.is_dict():
            for remote in value.get_dict().get("remote"):
                # Respect per-remote active flag (defaults to inactive if missing)
                if not self._is_active_flag(remote.get(ActiveConfigOption.get_name())):
                    continue
                repo = self._get_target_git_repo()

                remote_name = self._build_str_value(remote["name"])
                remote_url = self._build_str_value(remote["url"])

                self._created_remote[remote_name] = (
                    git_remote_create_once(repo, remote_name, remote_url) is not None
                )

    def _remotes_description(self) -> str:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        value = self.target.get_option_value(GitConfigOption)

        if not value or not value.is_dict():
            return ""

        remotes = value.get_dict().get("remote")
        if not remotes:
            return ""

        parts: list[str] = []
        for remote in remotes:
            try:
                name = self._build_value(remote.get("name"))
                url = self._build_value(remote.get("url"))
                if name and url:
                    parts.append(f"{name} -> {url}")
                elif name:
                    parts.append(str(name))
                elif url:
                    parts.append(str(url))
            except Exception:
                # Be conservative: if anything goes wrong computing description, skip that entry
                continue

        return ", ".join(parts)

    def _is_remote_missing_or_mismatched(self) -> bool:
        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        value = self.target.get_option_value(GitConfigOption)

        # If no value or no remotes key, we consider no need to apply here.
        if not value or not value.has_key_in_dict("remote"):
            return False

        # If any configured remote is missing by name or has a different URL, apply.
        repo = self._get_target_git_repo()

        configured_remotes = value.get_dict().get("remote", [])
        existing_by_name = {r.name: r for r in repo.remotes}

        for remote in configured_remotes:
            # Skip inactive remotes; treat missing flag as inactive
            if not self._is_active_flag(remote.get(ActiveConfigOption.get_name())):
                continue
            desired_name = self._build_value(remote.get("name"))
            desired_url = self._build_value(remote.get("url"))

            if not desired_name:
                # Malformed config, skip this entry
                continue

            existing = existing_by_name.get(str(desired_name))
            if existing is None:
                return True

            if desired_url:
                existing_urls = {u for u in existing.urls}
                if str(desired_url) not in existing_urls:
                    return True

        # All configured remotes exist with expected URLs
        return False

    def _get_target_git_repo(self) -> Repo:
        return Repo(self.target.get_path())

    def undo(self) -> None:
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )

        option = cast(GitConfigOption, self.target.get_option(GitConfigOption))

        config = option.get_value().get_dict()
        for remote in config.get("remote"):
            if self._created_remote:
                repo = self._get_target_git_repo()
                remote_name = (
                    self._build_value(remote["name"])
                    if not isinstance(remote["name"], str)
                    else remote["name"]
                )

                if self._created_remote[remote_name] is True:
                    repo.delete_remote(remote=repo.remote(name=remote_name))
