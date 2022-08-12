#!/usr/bin/env python3
# pylint: disable=invalid-name

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
import os
from typing import Any
from typing import Dict
from typing import Optional

import click
from nob import Nob

# from strictyaml import MapCombined
# from strictyaml import Int
# namespace collision: we're already using Any from typing.
from strictyaml import YAML
from strictyaml import Any as AnyYAML
from strictyaml import Bool
from strictyaml import EmptyNone
from strictyaml import Map
from strictyaml import MapPattern
from strictyaml import Optional as OptionalYAML
from strictyaml import Seq
from strictyaml import Str
from strictyaml import load
from strictyaml.exceptions import YAMLValidationError

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


def check_is_file(list_of_paths, key: Optional[str]):
    """For each item in a list, check that the value is a file.

    Args:
        list_of_paths: (list) List of strings or dictionaries
        key: (str) (optional) If dictionaries, this key matches the paths.

    """
    s = Settings()
    missing: list = []
    for item in list_of_paths:
        path: str = ""
        if isinstance(item, str):
            path = item
        elif isinstance(item, dict):
            if key is None:
                abort("List of paths is a dict, but no key (e.g. 'path') is provided.")
            else:
                path = item[key]
        else:
            abort("List of paths must contain either strings or dictionaries.")

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


def validate_key_include(c: YAML, config_path: str):
    """Validate config key: include.

    Example Format:

    include:
     - path: "INCLUDE_A.yaml"
     - path: "INCLUDE_B.yaml"
    """
    if c["include"].data:
        msg_validating_key("include")
        c["include"].revalidate(Seq(Map({"path": Str()})))
        check_is_file(c["include"].data, "path")


def validate_key_tables_config(c: YAML, config_path: str):
    """Validate config key: tables_config.

    Example Format:

    tables_config:
     TABLE_NAME_A:
       - path: SOURCE_A.xlsx
         sheet: SHEET A.1
         datetime:
           FIELD_1: NONE_OR_STR
           FIELD_2: NONE_OR_STR
         pivot:
           index: FIELD_ID
           columns: FIELD_KEY
           values: FIELD_VALUE
     TABLE_NAME_B:
       - path: SOURCE_B.csv
    """
    key: str = check_key("tables_config", c)
    if key:
        c[key].revalidate(MapPattern(Str(), Seq(AnyYAML())))
        for table_name in c[key].data:
            msg_validating_key(table_name)
            check_is_file(c[key][table_name].data, "path")
            table = c[key][table_name]
            table.revalidate(
                Seq(
                    Map(
                        {
                            "path": StrNotEmpty(),
                            OptionalYAML("sheet"): StrNotEmpty(),
                            OptionalYAML("datetime", drop_if_none=False): EmptyNone()
                            | AnyYAML(),
                            OptionalYAML("pivot", drop_if_none=False): EmptyNone()
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


def validate_key_create_tables(c: YAML, config_path: str):
    """Validate config key: create_tables.

    Example Format:

    create_tables:
     - TABLE_NAME_A
     - TABLE_NAME_B
    """
    key: str = check_key("create_tables", c)
    if key:
        for table in c[key].data:
            print("creating table: ", table)
        # TODO Check that tables exist in configuration object.


def check_key(key: str, c: YAML):
    """Check whether a key exists in configuration YAML.

    Args:
       key (str)   name of key
       c (YAML)    config YAML

    Returns:
       name of key (str) if present, None if not
    """
    if c[key].data:
        msg_validating_key(key)
        return key
    else:
        return None


def validate_key_import(c: YAML, config_path: str):
    """Validate config key: import.

    Example Format:

    import:
     - path: "MODULE_A.py"
     - path: "MODULE_B.py"
    """
    key: str = check_key("import", c)
    if key:
        c[key].revalidate(Seq(Map({"path": Str()})))
        check_is_file(c[key].data, "path")


def validate_key_input(c: YAML, config_path: str):
    """Validate config key: input.

    Example Format:

    input:
        strip: true
        slugify_columns: true
        lowercase_columns: true
    """
    key: str = check_key("input", c)
    if key:
        c[key].revalidate(
            Map(
                {
                    "strip": Bool(),
                    "slugify_columns": Bool(),
                    "lowercase_columns": Bool(),
                }
            )
        )


def validate_key_output(c: YAML, config_path: str):
    """Validate config key: output.

    Example Format:

    output:
        dir: output
        basename: BASENAME
        prepend_date: true
        export_tables: csv
        export_queries: csv
        styles:
            column_width: 15
    """
    key: str = check_key("output", c)
    if key:
        c[key].revalidate(
            Map(
                {
                    "dir": StrNotEmpty(),
                    "basename": StrNotEmpty(),
                    "prepend_date": Bool(),
                    # FIXME Use a sequence of allowed choices: csv | xlsx
                    "export_tables": Str(),
                    "export_queries": Str(),
                    "styles": AnyYAML(),
                }
            )
        )
        # FIXME Revalidate styles


def validate_key_queries(c: YAML, config_path: str):
    """Validate config key: queries.

    Example Format:

    queries:
    - name: QUERY A
      sql: |
      SELECT
      *
      FROM
      table_from_spreadsheet AS s
      ;

    - name: QUERY B
      df_postprocess: postprocess_df
      sql: |
      SELECT
      *
      FROM
      table_from_spreadsheet AS s
      JOIN
      table_from_csv AS c
      ON
      s.id = c.id
      ;
    """
    key: str = check_key("queries", c)
    if key:
        for query in c[key]:
            schema = Map(
                {
                    "name": StrNotEmpty(),
                    "sql": StrNotEmpty(),
                    OptionalYAML("df_postprocess"): StrNotEmpty(),
                }
            )
            revalidate_yaml(query, schema, config_path)


def revalidate_yaml(yaml: YAML, schema: Map | MapPattern, config_path: str):
    """Revalidate yaml from config_path according to schema.

    Args:
        yaml (YAML): yaml to revalidate
        schema (Map | MapPattern): schema to validate with
        config_path (str): file in which this YAML was found.
    """
    s = Settings()
    try:
        yaml.revalidate(schema)
    except YAMLValidationError as err:
        abort(s.MSG_INVALID_YAML, err, file_path=config_path)


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
            OptionalYAML("include", drop_if_none=False): EmptyNone() | AnyYAML(),
            OptionalYAML("tables_config", drop_if_none=False): EmptyNone() | AnyYAML(),
            OptionalYAML("create_tables", drop_if_none=False): EmptyNone() | Seq(Str()),
            OptionalYAML("import", drop_if_none=False): EmptyNone() | AnyYAML(),
            OptionalYAML("output", drop_if_none=False): EmptyNone() | AnyYAML(),
            OptionalYAML("input", drop_if_none=False): EmptyNone() | AnyYAML(),
            OptionalYAML("queries", drop_if_none=False): EmptyNone() | Seq(AnyYAML()),
        }
    )

    c = load_yaml_file(config_path, schema)

    validate_key_include(c, config_path)
    validate_key_tables_config(c, config_path)
    validate_key_create_tables(c, config_path)
    validate_key_import(c, config_path)
    validate_key_input(c, config_path)
    validate_key_output(c, config_path)
    validate_key_queries(c, config_path)

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
