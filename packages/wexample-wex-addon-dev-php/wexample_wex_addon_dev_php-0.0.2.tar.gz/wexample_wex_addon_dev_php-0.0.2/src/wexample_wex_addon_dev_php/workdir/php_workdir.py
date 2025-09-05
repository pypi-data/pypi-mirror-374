from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.children_file_factory_config_option import (
    ChildrenFileFactoryConfigOption,
)
from wexample_filestate.const.disk import DiskItemType
from wexample_wex_core.workdir.code_base_workdir import CodeBaseWorkdir


class PhpWorkdir(CodeBaseWorkdir):
    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        raw_value = super().prepare_value(raw_value=raw_value)
        from wexample_helpers.helpers.array import array_dict_get_by

        # Ensure a composer.json file exists for any PHP package project
        children = raw_value["children"]

        children.append(
            {
                "name": "composer.json",
                "type": DiskItemType.FILE,
                "should_exist": True,
            }
        )

        # Add rules to .gitignore
        array_dict_get_by("name", ".gitignore", children).setdefault(
            "should_contain_lines", []
        ).extend(
            [
                ".php-cs-fixer.cache",
                ".scannerwork",
                "/vendor",
            ]
        )

        return raw_value

    def get_dependencies(self) -> list[str]:
        # TODO search in composer.json
        return []

    def _create_php_file_children_filter(self) -> ChildrenFileFactoryConfigOption:
        from wexample_filestate.config_option.children_filter_config_option import (
            ChildrenFilterConfigOption,
        )
        from wexample_filestate.const.disk import DiskItemType
        from wexample_filestate_php.file.php_file import PhpFile

        return ChildrenFilterConfigOption(
            pattern={
                "class": PhpFile,
                "name_pattern": r"^.*\.php$",
                "type": DiskItemType.FILE,
                "python": [],
            },
            recursive=True,
        )
