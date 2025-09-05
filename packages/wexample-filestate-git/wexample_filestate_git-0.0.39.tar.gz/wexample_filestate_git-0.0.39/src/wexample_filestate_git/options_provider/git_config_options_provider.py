from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class GitConfigOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> list[type[AbstractConfigOption]]:
        from wexample_filestate.config_option.active_config_option import (
            ActiveConfigOption,
        )
        from wexample_filestate_git.config_option.main_branch_config_option import (
            MainBranchConfigOption,
        )
        from wexample_filestate_git.config_option.remote_config_option import (
            RemoteConfigOption,
        )

        return [
            ActiveConfigOption,
            MainBranchConfigOption,
            RemoteConfigOption,
        ]
