#!/usr/bin/env python3

"""Settings class."""


class Settings:
    """Define global settings.

    When you need a setting in a function, make an instance of this class.
    These settings should NOT be changed; treat them as constants.
    """

    PKG = "yarm"
    DEFAULT_CONFIG_FILE: str = "yarm.yaml"
    DIR_TEMPLATES: str = "templates"
    DIR_TESTS_DATA: str = "tests_data"

    ARG_VERBOSE: str = "verbose"

    EXT_YAML: str = ".yaml"

    TEST_CONFIG_BAD_YAML: str = "test_config_bad_yaml"
    TEST_CONFIG_BAD_OPTIONS: str = "test_config_bad_options"

    MSG_ABORT: str = "Failed."
    MSG_SUCCESS: str = "Success!"
    MSG_WARN: str = "Warning:"
    MSG_USAGE: str = "Usage:"

    MSG_CONFIG_FILE_NOT_FOUND: str = "Could not find config file:"
    MSG_DIRECTORY_ERROR: str = "Expected a file, but this is a directory:"
    MSG_PERMISSION_ERROR: str = "Permission denied."
    MSG_INVALID_CONFIG_NO_EDITS: str = (
        "This config file does not appear to have been edited."
    )
    MSG_INVALID_YAML: str = """This config file has invalid YAML or a misconfiguration.
Please fix the error below and try again."""
    MSG_INVALID_YAML_SCANNER: str = """This config file has invalid YAML.
Please fix the error below and try again. If there is a colon in your value,
try surrounding the entire value with single or double quote marks."""
    MSG_PATH_NOT_FOUND: str = "One or more paths in your config could not be found:"
    MSG_VALIDATING_KEY: str = "Validating"
    MSG_CONFIG_FILE_VALID: str = ">> Configuration file validated: "

    MSG_BEGIN_VALIDATING_FILE: str = "<< Begin validating file"
    MSG_INCLUDE_KEY: str = "Included from file"
    MSG_OVERIDE_KEY: str = "Overriden from file"
    MSG_INCLUDE_RETURN_PREV: str = "Returning to previous file"

    COLOR_ERROR: str = "red"
    COLOR_SUCCESS: str = "bright_green"
    COLOR_WARN: str = "bright_yellow"
    COLOR_DATA: str = "bright_cyan"

    TEST_CUSTOM_CONFIG_FILE: str = "custom.yaml"
    CMD_RUN = "run"

    CONFIG_SCHEMA = "config_schema.yaml"

    MSG_TEST_KEY_NOT_IN_SCHEMA: str = "key not in schema"
    MSG_TEST_EXPECTED_LIST: str = "found a mapping"
    MSG_MISSING_REQUIRED_KEY: str = "Missing required key(s):"
    MSG_NL: str = "\n"
    MSG_NL_TAB: str = "\n   "
    MSG_TAB: str = "   "
    MSG_LINE: str = "------------------------------------------------"
    MSG_LINE_DOUBLE: str = "================================================"
    MSG_NEED_EXPORT_TABLES_OR_QUERIES: str = """
No queries found. We need something to output!
    Please either:
    - Define one or more queries under "queries:"
    - Or set "output: export_tables" to "csv" or "xlsx"."""
    MSG_EXPORT_TABLES_ONLY: str = (
        "No queries found, but 'output: export_tables' is set. Will output tables to"
    )

    MSG_CONNECTION_DATABASE_FAILED: str = "Failed to connect to database."
    MSG_SQLITE_ERROR: str = "There was a problem with sqlite:"

    MSG_CREATING_TABLE: str = "Creating table"
    MSG_CREATED_TABLE: str = "Table created"
    MSG_IMPORTING_DATA: str = "Importing data from"
    MSG_IMPORTING_SHEET: str = "Importing sheet"
    MSG_STRIP_WHITESPACE: str = (
        "Stripping whitespace at start and end of all strings..."
    )
    MSG_SLUGIFY_COLUMNS: str = "Slugifying all columns..."
    MSG_LOWERCASE_COLUMNS: str = "Lowercasing all columns..."
    MSG_UPPERCASE_ROWS: str = "Uppercasing all rows..."
    MSG_APPLYING_PIVOT: str = "Applying pivot"
    MSG_MERGING_PATH: str = "Merging path"
    MSG_MERGE_ERROR: str = "Merge error: No common column to merge on with table"
    MSG_MERGE_ERROR_PS: str = """Remember: merge column names are...
    - case-sensitive (unless you set lowercase_columns = true)
    - must be spelled the same in every path."""
    MSG_MERGE_TYPE_ERROR: str = "Type error while merging table"
    MSG_CONVERTING_DATETIME: str = "Converting field(s) to datetime:"

    MSG_SHOW_DF: str = "Dataframe"
    MSG_NO_SHEET_PROVIDED: str = "No 'sheet' key provided, importing first sheet from"
    MSG_BAD_FILE_EXT: str = "Bad file extension in"
    MSG_CREATE_TABLE_DATABASE_ERROR: str = "Database Error: Could not create table"
    MSG_CREATE_TABLE_VALUE_ERROR: str = "Value Error: Could not create table"
    MSG_MISSING_DATETIME: str = "Column under 'datetime:' not found"
    MSG_PIVOT_FAILED_KEY_ERROR: str = "Pivot failed, because this column is missing"

    # NOTE These keys are for use with Nob objects, not for validating YAML schemas.
    KEY_TABLES_CONFIG = "/tables_config"
    KEY_OUTPUT__BASENAME = "/output/basename"
    KEY_OUTPUT__DIR = "/output/dir"
    KEY_INPUT = "/input"
    KEY_INPUT__STRIP = "/input/strip"
    KEY_INPUT__SLUGIFY_COLUMNS = "/input/slugify_columns"
    KEY_INPUT__LOWERCASE_COLUMNS = "/input/lowercase_columns"
    KEY_INPUT__UPPERCASE_ROWS = "/input/uppercase_rows"
    KEY_OUTPUT__EXPORT_TABLES = "/output/export_tables"
    KEY_QUERIES = "/queries"
    KEY_SHEET = "sheet"

    # tables_config keys. They are deep in the path, so do not use /.
    KEY_PIVOT = "pivot"
    # The schema ensures that each pivot key has one of each of these:
    KEY_PIVOT_INDEX = "index"
    KEY_PIVOT_COLUMNS = "columns"
    KEY_PIVOT_VALUES = "values"

    KEY_DATETIME = "datetime"

    CSV = "csv"
    XLSX = "xlsx"
