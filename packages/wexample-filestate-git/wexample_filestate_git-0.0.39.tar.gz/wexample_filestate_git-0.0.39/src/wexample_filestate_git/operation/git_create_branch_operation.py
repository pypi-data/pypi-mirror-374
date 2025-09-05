from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate_git.operation.abstract_git_operation import AbstractGitOperation

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class GitCreateBranchOperation(FileManipulationOperationMixin, AbstractGitOperation):
    def description(self) -> str:
        return "Create local Git branch if missing"

    def dependencies(self):
        # Ensure repository is initialized before creating a branch
        from wexample_filestate_git.operation.git_init_operation import GitInitOperation

        return [GitInitOperation]  # type: ignore[return-value]

    def applicable_for_option(self, option: AbstractConfigOption) -> bool:
        # Only applicable when git is enabled and repo exists
        if not self._is_active_git_option(option):
            return False

        if not option.should_have_git():
            return False

        # Determine desired branch name from config
        branch = self._get_desired_branch_name()
        if not branch:
            return False

        repo = self._get_target_git_repo()

        # Apply only if the branch does not exist locally
        return not any(h.name == branch for h in getattr(repo, "heads", []))

    def describe_before(self) -> str:
        branch = self._get_desired_branch_name() or "<unknown>"
        return f"Local branch missing: {branch}"

    def describe_after(self) -> str:
        branch = self._get_desired_branch_name() or "<unknown>"
        return f"Local branch created: {branch}"

    def apply(self) -> None:
        """Create the desired branch locally if it does not exist.

        Notes:
        - This operation is local-only (no remote push, no deletion/rename of other branches).
        - The branch is created at current HEAD.
        """
        branch = self._get_desired_branch_name()
        if not branch:
            return

        repo = self._get_target_git_repo()
        if any(h.name == branch for h in getattr(repo, "heads", [])):
            return  # Already exists

        # Create new branch at current HEAD
        repo.create_head(branch)

    # --- helpers ---
    def _get_desired_branch_name(self) -> str | None:
        """Resolve desired branch name from config.

        Accepts either a list (first item) or a single string value.
        Defaults to "main" if the option exists but is empty/invalid.
        """
        from wexample_filestate_git.config_option.git_config_option import (
            GitConfigOption,
        )
        from wexample_filestate_git.config_option.main_branch_config_option import (
            MainBranchConfigOption,
        )

        git_option = self.target.get_option(GitConfigOption)
        if not git_option:
            return None

        main_opt = git_option.get_option(MainBranchConfigOption)
        if not main_opt:
            return None

        v = main_opt.get_value()

        # Prefer list form
        if v.is_list():
            items = v.get_list()
            first = items[0]
            if isinstance(first, str):
                return first

            # If not plain string, try to coerce via build_value
            return self._build_str_value(first)

        # Fallback: single string value
        if v.is_str():
            return v.get_str()

        if isinstance(v, str):
            return v

        # If the option exists but has no usable value, default to "main"
        return "main"

    def undo(self) -> None:
        # No destructive undo: we do not auto-delete newly created branches
        pass
