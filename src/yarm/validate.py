#!/usr/bin/env python3
# pylint: disable=invalid-name

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
import os
from typing import Any
from typing import Dict

import click
from nob import Nob

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
from strictyaml import load

from yarm.helpers import abort
from yarm.helpers import load_yaml_file

# from yarm.helpers import warn
from yarm.settings import Settings


# from typing import List


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
    c = Nob(config.data)
    if "/output/basename" in c:
        if c.output.basename == default_config.output.basename:
            abort(
                f"""{s.MSG_INVALID_CONFIG_NO_EDITS}
    output.basename is still set to the default: {default_config.output.basename}
    Please edit your config file, then try running this report again."""
            )


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
        """Invalidate if string is empty."""
        if any([chunk.contents == ""]):
            chunk.expecting_but_found("when expecting a string that is not empty")
        return chunk.contents


def msg_validating_key(key: str):
    """Show a message that a key is being validated."""
    s = Settings()
    click.echo(s.MSG_VALIDATING_KEY, nl=False)
    click.secho(key, fg=s.COLOR_DATA)
    # TODO Only show if verbose


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

    c = load_yaml_file(config_path, schema)

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
        msg_validating_key("tables_config")
        c["tables_config"].revalidate(MapPattern(Str(), Seq(AnyYAML())))
        for table_name in c["tables_config"].data:
            msg_validating_key(table_name)
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
    click.echo(s.MSG_CONFIG_FILE_VALID, nl=False)
    click.secho(config_path, fg=s.COLOR_DATA)
    return c


def get_default_config() -> Nob:
    """Get default config."""
    s = Settings()
    return Nob(
        load(
            pkg_resources.read_text(
                f"{s.PKG}.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE
            ),
        ).data
    )


def get_first_dict_key(dict_to_extract: Dict[Any, Any]) -> Any:
    """Return the first key in a dictionary."""
    return list(dict_to_extract.items())[0][0]
