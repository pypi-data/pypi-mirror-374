from __future__ import annotations

from types import UnionType

from wexample_config.config_option.abstract_list_config_option import (
    AbstractListConfigOption,
)


class MainBranchConfigOption(AbstractListConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> type | UnionType:
        return str
