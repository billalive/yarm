#!/usr/bin/env python3
# pylint: disable=invalid-name

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
import os
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import click
from nob import Nob

# from strictyaml import MapCombined
# namespace collision: we're already using Any from typing.
from strictyaml import YAML
from strictyaml import Any as AnyYAML
from strictyaml import Bool
from strictyaml import EmptyNone
from strictyaml import Enum
from strictyaml import Int
from strictyaml import Map
from strictyaml import MapPattern
from strictyaml import Optional as OptionalYAML
from strictyaml import Seq
from strictyaml import Str
from strictyaml import load
from strictyaml.exceptions import YAMLValidationError

from yarm.helpers import abort
from yarm.helpers import load_yaml_file
from yarm.helpers import msg_with_data

# from yarm.helpers import warn
from yarm.settings import Settings


# from typing import List


def default_config() -> YAML:
    """Define default configuration options.

    These options can be overridden by config file(s).

    Returns:
        config (YAML): default config as YAML.
    """
    config: YAML = load(
        """
    output:
      dir: output
    """
    )
    return config


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

    prev = default_config()
    config = validate_config_schema(config_path, prev)
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


def msg_validating_key(key: str, suffix: str = None):
    """Show a message that a key is being validated."""
    s = Settings()
    msg = s.MSG_VALIDATING_KEY
    if suffix:
        msg += " "
        msg += suffix
    msg_with_data(msg, key)
    # TODO Only show if verbose


def validate_key_include(c: YAML, config_path: str, prev: YAML):
    """Validate config key: include.

    Example Format:

    include:
     - path: INCLUDE_A.yaml
     - path: INCLUDE_B.yaml

    Recurse over each path and validate it as config.

    Args:
        c (YAML): new config to validate
        config_path (str): path to config file to include.
        prev (YAML): previous config that has already been validated

    Returns:
        updated_config (YAML): updated config
    """
    s = Settings()
    key: str = check_key("include", c)
    key_path: str = "path"
    updated_config = YAML("")
    if key:
        schema = Seq(Map({key_path: StrNotEmpty()}))
        revalidate_yaml(c[key], schema, config_path)
        check_is_file(c[key].data, key_path)
        for include in c[key]:
            # FIXME How do I update prev (previous config) on each recursive call of
            # validate_config_schema? Simply updating update_config is not enough.
            updated_config = validate_config_schema(include[key_path].data, prev)
        msg_with_data(s.MSG_INCLUDE_RETURN_PREV, config_path)
    else:
        updated_config = c
    return updated_config


def validate_key_tables_config(c: YAML, config_path: str, prev: YAML):
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
        schema = MapPattern(Str(), Seq(AnyYAML()))
        revalidate_yaml(c[key], schema, config_path)
        for table_name in c[key].data:
            table = c[key][table_name]
            schema = Seq(
                Map(
                    {
                        "path": StrNotEmpty(),
                        OptionalYAML("sheet"): StrNotEmpty(),
                        OptionalYAML("datetime"): EmptyNone() | AnyYAML(),
                        OptionalYAML("pivot"): EmptyNone() | AnyYAML(),
                    }
                )
            )
            revalidate_yaml(table, schema, config_path, table_name, "table")
            check_is_file(c[key][table_name].data, "path")
            # datetime:
            for source in table:
                if "datetime" in source:
                    schema = MapPattern(Str(), EmptyNone() | Str())
                    revalidate_yaml(
                        source["datetime"],
                        schema,
                        config_path,
                        f"{table_name}: datetime",
                    )
                if "pivot" in source:
                    schema = Map(
                        {
                            "index": StrNotEmpty(),
                            "columns": StrNotEmpty(),
                            "values": StrNotEmpty(),
                        }
                    )
                    revalidate_yaml(
                        source["pivot"], schema, config_path, f"{table_name}: pivot"
                    )


def validate_key_create_tables(c: YAML, config_path: str, prev: YAML):
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
    if key in c:
        msg_validating_key(key)
        return key
    else:
        return None


def validate_key_import(c: YAML, config_path: str, prev: YAML):
    """Validate config key: import.

    Example Format:

    import:
     - path: "MODULE_A.py"
     - path: "MODULE_B.py"
    """
    key: str = check_key("import", c)
    if key:
        schema = Seq(Map({"path": StrNotEmpty()}))
        revalidate_yaml(c[key], schema, config_path)
        check_is_file(c[key].data, "path")


def validate_key_input(c: YAML, config_path: str, prev: YAML):
    """Validate config key: input.

    Example Format:

    input:
        strip: true
        slugify_columns: true
        lowercase_columns: true
    """
    key: str = check_key("input", c)
    if key:
        schema = Map(
            {
                OptionalYAML("strip"): Bool(),
                OptionalYAML("slugify_columns"): Bool(),
                OptionalYAML("lowercase_columns"): Bool(),
            }
        )
        revalidate_yaml(c[key], schema, config_path)


def validate_key_output(c: YAML, config_path: str, prev: YAML):
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
        schema = Map(
            {
                "basename": StrNotEmpty(),
                OptionalYAML("dir"): StrNotEmpty(),
                OptionalYAML("prepend_date"): Bool(),
                OptionalYAML("export_tables"): Enum(["csv", "xlsx"]),
                OptionalYAML("export_queries"): Enum(["csv", "xlsx"]),
                OptionalYAML("styles"): AnyYAML(),
            }
        )
        revalidate_yaml(c[key], schema, config_path)
        if "styles" in c[key]:
            schema = Map(
                {
                    "column_width": Int(),
                }
            )
            revalidate_yaml(c[key]["styles"], schema, config_path, "output.styles")


def validate_key_queries(c: YAML, config_path: str, prev: YAML):
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
      replace:
        FIELD_A:
          MATCH A1: REPLACE A1
          MATCH A2: REPLACE A2
        FIELD_B:
          MATCH B1: REPLACE B1
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
                    OptionalYAML("replace"): AnyYAML(),
                }
            )
            revalidate_yaml(query, schema, config_path)
            if "replace" in query:
                schema = MapPattern(Str(), AnyYAML())
                revalidate_yaml(
                    query["replace"], schema, config_path, f"{query['name']}: replace"
                )
                for field in query["replace"]:
                    schema = MapPattern(Str(), Str())
                    revalidate_yaml(query["replace"][field], schema, config_path)
                    # for match in query["replace"][field]:
                    #     print(
                    #         "field:",
                    #         field,
                    #         "match:",
                    #         match,
                    #         "replace with:",
                    #         query["replace"][field][match].data,
                    #     )


def revalidate_yaml(
    yaml: YAML,
    schema: Union[Map, MapPattern],
    config_path: str,
    msg_key: Union[str, None] = None,
    msg_suffix: Union[str, None] = None,
):
    """Revalidate yaml from config_path according to schema.

    Args:
        yaml (YAML): yaml to revalidate
        schema (Map | MapPattern): schema to validate with
        config_path (str): file in which this YAML was found.
        msg_key (str): (optional) if provided, message that this key is validating.
        msg_suffix (str): (optional) message suffix
    """
    s = Settings()
    try:
        if msg_key:
            if msg_suffix:
                msg_validating_key(msg_key, msg_suffix)
            else:
                msg_validating_key(msg_key)
        yaml.revalidate(schema)
    except YAMLValidationError as err:
        abort(s.MSG_INVALID_YAML, err, file_path=config_path)


def validate_config_schema(config_path: str, prev: YAML) -> Any:
    """Return YAML for config file if it validates agaist schema.

    Args:
        config_path (str): Path to config file
        prev (YAML): previous config that may be overridden

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
            OptionalYAML("include"): EmptyNone() | AnyYAML(),
            OptionalYAML("tables_config"): EmptyNone() | AnyYAML(),
            OptionalYAML("create_tables"): EmptyNone() | Seq(StrNotEmpty()),
            OptionalYAML("import"): EmptyNone() | AnyYAML(),
            OptionalYAML("output"): EmptyNone() | AnyYAML(),
            OptionalYAML("input"): EmptyNone() | AnyYAML(),
            OptionalYAML("queries"): EmptyNone() | Seq(AnyYAML()),
        }
    )

    new_config = load_yaml_file(config_path, schema)

    msg_with_data(s.MSG_BEGIN_VALIDATING_FILE, config_path)

    for func in [
        # NOTE Validate include FIRST, so later functions can override included config.
        "validate_key_include",
        "validate_key_tables_config",
        "validate_key_create_tables",
        "validate_key_import",
        "validate_key_input",
        "validate_key_output",
        "validate_key_queries",
    ]:
        updated_config = globals()[func](new_config, config_path, prev)

    click.echo(s.MSG_CONFIG_FILE_VALID, nl=False)
    click.secho(config_path, fg=s.COLOR_DATA)

    # If configuration validates, return config object.
    return updated_config


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
