#!/usr/bin/env python3
# pylint: disable=invalid-name

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
import importlib.util
import os
import re
import sys

# from typing import Dict
from typing import Any
from typing import Optional
from typing import Union

from nob import Nob
from slugify import slugify

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
from strictyaml import ScalarValidator
from strictyaml import Seq
from strictyaml import Str
from strictyaml import load
from strictyaml.exceptions import YAMLValidationError
from strictyaml.yamllocation import YAMLChunk

from yarm.helpers import abort
from yarm.helpers import load_yaml_file
from yarm.helpers import msg_with_data
from yarm.helpers import verbose_ge

# from yarm.helpers import warn
from yarm.settings import Settings


class Slug(ScalarValidator):
    """Class to use slugify to make spelling consistent."""

    def validate_scalar(self, chunk):
        """Use slugify to make spelling consistent.

        Use _ rather than - for separator; it's more Pythonic.

        Also, Ansible config files seem to favor underscores, see:
        https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
        """
        return slugify(chunk.contents, separator="_")


def validate_config(config_path: str) -> YAML:
    """Validate config file before running report.

    Args:
        config_path (str): Path to config file

    Returns:
        config (YAML): validated config as YAML

    """
    # Why no test for whether file exists? Because click() handles this.

    # DEBUG:
    # for key in config:
    #    print(key, config[key])

    config = validate_config_schema(config_path)

    # Check whether config file has been edited.
    validate_config_edited(config)

    # Check whether minimum required keys are present.
    validate_minimum_required_keys(config)

    # If all tests pass, config file is validated.
    return config


def validate_config_edited(config: YAML) -> bool:
    """Check whether config has been edited."""
    # Rather than an exhaustive search, just check a critical setting.
    s = Settings()
    default_config = get_default_config()
    c = Nob(config.data)
    if s.KEY_OUTPUT__BASENAME in c:
        if c[s.KEY_OUTPUT__BASENAME] == default_config[s.KEY_OUTPUT__BASENAME]:
            abort(
                f"""{s.MSG_INVALID_CONFIG_NO_EDITS}
    output.basename is still set to the default: {default_config.output.basename}
    Please edit your config file, then try running this report again."""
            )
    return True


def validate_minimum_required_keys(config: YAML) -> bool:
    """Check whether config has minimum required keys."""
    s = Settings()
    c = Nob(config.data)
    missing_keys = []
    for key in [
        s.KEY_TABLES_CONFIG,
        s.KEY_OUTPUT__BASENAME,
        s.KEY_OUTPUT__DIR,
    ]:
        if key not in c:
            display_key: str = re.sub("^/", "", key)
            display_key = re.sub("/", ": ", display_key)
            missing_keys.append(display_key)
    if len(missing_keys) > 0:
        abort(
            f"{s.MSG_MISSING_REQUIRED_KEY}{s.MSG_NL_TAB}{s.MSG_NL_TAB.join(missing_keys)}"
        )

    # To generate output, we need either queries: or export_tables:
    if s.KEY_QUERIES not in c:
        if s.KEY_OUTPUT__EXPORT_TABLES not in c:
            abort(s.MSG_NEED_EXPORT_TABLES_OR_QUERIES)
        else:
            msg_with_data(s.MSG_EXPORT_TABLES_ONLY, c[s.KEY_OUTPUT__EXPORT_TABLES][:])
    return True


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
        # NOTE These abort() calls can only be triggered by incorrectly calling this
        # function, not by config, so we don't need to test them with coverage.
        if isinstance(item, str):
            path = item  # pragma: no cover
        elif isinstance(item, dict):
            if key is None:
                abort(
                    "List of paths is a dict, but no key (e.g. 'path') is provided."
                )  # pragma: no cover
            else:
                path = item[key]
        else:
            abort(
                "List of paths must contain either strings or dictionaries."
            )  # pragma: no cover

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
    def validate_scalar(chunk: YAMLChunk) -> str:
        """Invalidate if string is empty."""
        if any([chunk.contents == ""]):
            chunk.expecting_but_found("when expecting a string that is not empty")
        return chunk.contents


def msg_validating_key(key: str, suffix: str = None, verbose: int = 1):
    """Show a message that a key is being validated."""
    s = Settings()
    if verbose_ge(verbose):
        msg = s.MSG_VALIDATING_KEY
        if suffix:
            msg += " "
            msg += suffix
        msg_with_data(msg, key, verbose=verbose)


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
         include_index: false
     TABLE_NAME_B:
       - path: SOURCE_B.csv
    """
    s = Settings()
    key: str = check_key("tables_config", c)
    if key:
        # Do not use Slug() on table names, because user will expect to use
        # their table names in their queries.
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
                        OptionalYAML("include_index"): Bool(),
                    },
                    key_validator=Slug(),
                )
            )
            revalidate_yaml(table, schema, config_path, table_name, "table")
            check_is_file(c[key][table_name].data, "path")

            include_index_defined: bool = False
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
                        },
                        key_validator=Slug(),
                    )
                    revalidate_yaml(
                        source["pivot"], schema, config_path, f"{table_name}: pivot"
                    )
                if "include_index" in source:
                    # Because a table is a list of paths, it is possible for more
                    # than one path to define include_index, which is unfortunate.
                    if not include_index_defined:
                        include_index_defined = True
                    else:
                        abort(
                            s.MSG_INCLUDE_INDEX_TABLE_CONFLICT,
                            data=table_name,
                            ps=s.MSG_INCLUDE_INDEX_TABLE_CONFLICT_PS,
                        )


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


def validate_key_import(c: YAML, config_path: str):
    """Validate config key: import.

    Example Format:

    import:
     - path: MODULE_A.py
     - path: MODULE_B.py

    If more than one module in this list defines the same function,
    the later module will silently override the previous definition.
    """
    s = Settings()
    key: str = check_key("import", c)
    if key:
        schema = Seq(Map({"path": StrNotEmpty()}, key_validator=Slug()))
        revalidate_yaml(c[key], schema, config_path)
        check_is_file(c[key].data, "path")
        for source in c[key]:
            file_path = source[s.KEY_MODULE__PATH].data
            msg_with_data(s.MSG_IMPORTING_MODULE_PATH, data=file_path, indent=1)
            module_name = s.IMPORT_MODULE_NAME
            # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
            spec = importlib.util.spec_from_file_location(module_name, file_path)  # type: ignore  # noqa:B950
            module = importlib.util.module_from_spec(spec)  # type: ignore
            sys.modules[module_name] = module
            spec.loader.exec_module(module)  # type: ignore


def validate_key_input(c: YAML, config_path: str):
    """Validate config key: input.

    Example Format:

    input:
        strip: true
        slugify_columns: true
        lowercase_columns: true
        uppercase_rows: true
        include_index: true
    """
    key: str = check_key("input", c)
    if key:
        schema = Map(
            {
                OptionalYAML("strip"): Bool(),
                OptionalYAML("slugify_columns"): Bool(),
                OptionalYAML("lowercase_columns"): Bool(),
                OptionalYAML("uppercase_rows"): Bool(),
                OptionalYAML("include_index"): Bool(),
            },
            key_validator=Slug(),
        )
        revalidate_yaml(c[key], schema, config_path)


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
    s = Settings()
    key: str = check_key("output", c)
    if key:
        schema = Map(
            {
                "basename": StrNotEmpty(),
                OptionalYAML("dir"): StrNotEmpty(),
                OptionalYAML("prepend_date"): Bool(),
                OptionalYAML("export_tables"): Enum(s.SCHEMA_EXPORT_FORMATS),
                OptionalYAML("export_queries"): Enum(s.SCHEMA_EXPORT_FORMATS),
                OptionalYAML("styles"): AnyYAML(),
            },
            key_validator=Slug(),
        )
        revalidate_yaml(c[key], schema, config_path)
        if "styles" in c[key]:
            schema = Map(
                {
                    "column_width": Int(),
                },
                key_validator=Slug(),
            )
            revalidate_yaml(c[key]["styles"], schema, config_path, "output.styles")
        validate_key_output_dir(c)


def validate_key_output_dir(c: YAML):
    """Prepare output directory."""
    s = Settings()
    config: Nob = Nob(c.data)
    output_dir = os.fspath(config[s.KEY_OUTPUT__DIR][:])
    if not os.path.isdir(output_dir):
        if os.path.exists(output_dir):
            abort(s.MSG_CANT_CREATE_OUTPUT_DIR, data=output_dir)
        else:
            msg_with_data(s.MSG_CREATING_OUTPUT_DIR, data=output_dir)
            os.makedirs(output_dir)
    else:
        msg_with_data(s.MSG_OUTPUT_DIR_EXISTS, data=output_dir, verbose=2)
    msg_with_data(s.MSG_OUTPUT_DIR, data=output_dir)


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
      postprocess: postprocess_function
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
    s = Settings()
    key: str = check_key("queries", c)
    if key:
        for query in c[key]:
            schema = Map(
                {
                    "name": StrNotEmpty(),
                    "sql": StrNotEmpty(),
                    OptionalYAML("postprocess"): StrNotEmpty(),
                    OptionalYAML("replace"): AnyYAML(),
                },
                key_validator=Slug(),
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

            if "postprocess" in query:
                if "import" not in c:
                    abort(
                        s.MSG_POSTPROCESS_BUT_NO_IMPORT,
                        data=query["postprocess"][:],
                        ps=s.MSG_POSTPROCESS_BUT_NO_IMPORT_PS,
                    )


def revalidate_yaml(
    yaml: YAML,
    schema: Union[Map, MapPattern, Seq],
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
                msg_validating_key(msg_key, msg_suffix, verbose=2)
            else:
                msg_validating_key(msg_key, verbose=2)
        yaml.revalidate(schema)
    except YAMLValidationError as err:
        abort(s.MSG_INVALID_YAML, err, file_path=config_path)


def validate_config_schema(config_path: str) -> Any:
    """Return YAML for config file if it validates agaist schema.

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
    #
    # TODO Uncoment include and create_tables when we implement these options.
    schema = Map(
        {
            # OptionalYAML("include"): EmptyNone() | AnyYAML(),
            OptionalYAML("tables_config"): EmptyNone() | AnyYAML(),
            # OptionalYAML("create_tables"): EmptyNone() | Seq(StrNotEmpty()),
            OptionalYAML("import"): EmptyNone() | AnyYAML(),
            OptionalYAML("output"): EmptyNone() | AnyYAML(),
            OptionalYAML("input"): EmptyNone() | AnyYAML(),
            OptionalYAML("queries"): EmptyNone() | Seq(AnyYAML()),
        },
        key_validator=Slug(),
    )

    c = load_yaml_file(config_path, schema)

    msg_with_data(s.MSG_BEGIN_VALIDATING_FILE, config_path, verbose=2)

    # TODO Uncoment include and create_tables when we implement these options.
    # validate_key_include(c, config_path)
    validate_key_tables_config(c, config_path)
    # validate_key_create_tables(c, config_path)
    validate_key_import(c, config_path)
    validate_key_input(c, config_path)
    validate_key_output(c, config_path)
    validate_key_queries(c, config_path)

    msg_with_data(s.MSG_CONFIG_FILE_VALID, config_path, verbose=2)

    # If configuration validates, return config object.
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
