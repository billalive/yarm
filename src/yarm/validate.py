#!/usr/bin/env python3
# pylint: disable=invalid-name

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
import os
from typing import Any
from typing import Dict

from path import Path

# from strictyaml import MapCombined
# from strictyaml import Int
# namespace collision: we're already using Any from typing.
from strictyaml import YAML
from strictyaml import Any as AnyYAML
from strictyaml import EmptyNone
from strictyaml import Map
from strictyaml import MapPattern
from strictyaml import Optional
from strictyaml import Seq
from strictyaml import Str
from strictyaml import YAMLError
from strictyaml import load

from yarm.helpers import abort

# from yarm.helpers import success
# from yarm.helpers import warn
# from yarm.helpers import yaml_to_dict
from yarm.settings import Settings


# from typing import List


# from yarm.helpers import echo_verbose


def validate_config(config_path: str) -> YAML:
    """Validate config file before running report.

    Args:
        config_path (str): Path to config file

    Returns:
        config (YAML): validated config as YAML

    """
    # Why no test whether file exists? click() handles this.

    # DEBUG:
    # for key in config:
    #    print(key, config[key])

    config = validate_config_schema(config_path)
    validate_config_edited(config)

    # Check whether config options are valid.

    # If all tests pass, config file is validated.
    return config


def validate_config_edited(config: YAML) -> bool:
    """Check whether config has been edited."""
    # Rather than an exhaustive search, just check a critical setting.
    s = Settings()
    default_config = get_default_config()
    if config["output"]["basename"] == default_config["output"]["basename"]:
        abort(
            f"""{s.MSG_INVALID_CONFIG_NO_EDITS}
output.basename is still set to the default: {default_config["output"]["basename"]}
Please edit your config file, then try running this report again."""
        )
    return True


def check_is_file(list_of_paths, key):
    """For each item with key (e.g. 'path'), check that the value is a file."""
    s = Settings()
    missing: list = []
    for item in list_of_paths:
        path = item[key]
        result = True
        if not os.path.exists(path):
            missing.append(path)
            result = False
    if not result:
        file_path: str = "\n".join(map(str, missing))
        abort(f"{s.MSG_PATH_NOT_FOUND}\n{file_path}")


class StrNotEmpty(Str):
    """A string that must not be empty."""

    @staticmethod
    def validate_scalar(chunk: str) -> str:
        """String does not validate if it is empty."""
        if any([chunk.contents == ""]):
            chunk.expecting_but_found("when expecting a string that is not empty")
        return chunk.contents


def validate_config_schema(config_path: str) -> Any:
    """Return config file if it validates agaist schema.

    Args:
        config_path (str): Path to config file

    Returns:
        config (YAML): validated config as YAML

    """
    s = Settings()
    # During initial validation, all fields are Optional because they
    # may be spread across multiple included files.
    # Once we have processed all config files, we will check separately that
    # all critical config items have been provided.
    schema = Map(
        {
            Optional("tables_config", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("create_tables", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("include", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("output", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("import_module", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("import", drop_if_none=False): EmptyNone() | AnyYAML(),
            Optional("queries", drop_if_none=False): EmptyNone() | AnyYAML(),
        }
    )

    try:
        c = load(Path(config_path).read_text(), schema)
    except YAMLError as error:
        abort(s.MSG_INVALID_YAML, error=error, file_path=config_path)
    except FileNotFoundError:
        abort(s.MSG_CONFIG_FILE_NOT_FOUND, file_path=config_path)

    # tables_config:
    #  TABLE_NAME_01:
    #    - path: "PATH_01.csv"
    #      sheet: "SHEET NAME"
    #      datetime:
    #        FIELD_01: NONE_OR_STR
    #        FIELD_02: NONE_OR_STR
    #      pivot:
    #        index: FIELD_ID
    #        columns: FIELD_KEY
    #        values: FIELD_VALUE
    if c["tables_config"].data:
        print("Validating tables_config")
        c["tables_config"].revalidate(MapPattern(Str(), Seq(AnyYAML())))
        for table_name in c["tables_config"].data:
            check_is_file(c["tables_config"][table_name].data, "path")
            table = c["tables_config"][table_name]
            table.revalidate(
                Seq(
                    Map(
                        {
                            "path": StrNotEmpty(),
                            Optional("sheet"): StrNotEmpty(),
                            Optional("datetime", drop_if_none=False): EmptyNone()
                            | AnyYAML(),
                            Optional("pivot", drop_if_none=False): EmptyNone()
                            | AnyYAML(),
                        }
                    )
                )
            )
            # datetime:
            for source in table:
                if source["datetime"].data:
                    source["datetime"].revalidate(
                        MapPattern(Str(), EmptyNone() | AnyYAML())
                    )
                if source["pivot"].data:
                    source["pivot"].revalidate(
                        Map(
                            {
                                "index": StrNotEmpty(),
                                "columns": StrNotEmpty(),
                                "values": StrNotEmpty(),
                            }
                        )
                    )

    # include:
    #  - path: "INCLUDE_PATH_01.yaml"
    #  - path: "INCLUDE_PATH_02.yaml"
    if c["include"].data:
        c["include"].revalidate(Seq(Map({"path": Str()})))
        check_is_file(c["include"].data, "path")

    # If configuration validates, return config object.
    return c


def get_default_config() -> Any:
    """Get default config."""
    s = Settings()
    return load(
        pkg_resources.read_text(f"{s.PKG}.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE),
    )


def get_config_schema() -> Any:
    """Get 'schema' of config options.

    When you add an option, you must add it to this template file,
    so that validate_config_schema() will recognize it.


    tables_config and create_tables should have identical options.

    Except: where tables_config has TABLE_NAME, create_tables has NONE_OR_LIST.
    This allows you to define a table fully

    They are separate so that you can include a config file with a tables_config
    that defines ALL the tables you often use, but then use create_tables to only
    actually create the specific tables you need for this report.
    """
    s = Settings()
    return load(
        pkg_resources.read_text(f"{s.PKG}.{s.DIR_TEMPLATES}", s.CONFIG_SCHEMA),
    )


def get_first_dict_key(dict_to_extract: Dict[Any, Any]) -> Any:
    """Return the first key in a dictionary."""
    return list(dict_to_extract.items())[0][0]
