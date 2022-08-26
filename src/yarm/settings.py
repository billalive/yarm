#!/usr/bin/env python3

"""Settings class."""


class Settings:
    """Define global settings.

    When you need a setting in a function, make an instance of this class.
    These settings should **not** be changed elsewhere. Treat them as constants.
    """

    PKG = "yarm"
    DEFAULT_CONFIG_FILE: str = "yarm.yaml"
    DIR_TEMPLATES: str = "templates"
    DIR_TESTS_DATA: str = "tests_data"

    ARG_VERBOSE: str = "verbose"
    ARG_EXPORT_DATABASE: str = "database"
    ARG_FORCE: str = "force"

    # Maximum number of -v switches.
    MAX_VERBOSE = 3
    MSG_MAX_VERBOSE_ERROR = "Maximum verbosity level is"

    EXT_YAML: str = ".yaml"

    TEST_CONFIG_BAD_YAML: str = "test_config_bad_yaml"
    TEST_CONFIG_BAD_OPTIONS: str = "test_config_bad_options"
    DEFAULT_TEST: str = "test_validate_complete_config_valid"

    MSG_ABORT: str = "Failed."
    MSG_SUCCESS: str = "Success!"
    MSG_WARN: str = "Warning:"
    MSG_USAGE: str = "Usage:"

    # new
    MSG_NEW_CONFIG_FILE_WRITTEN: str = "New config file written to"
    MSG_NEW_CONFIG_FILE_WRITTEN_PS: str = "To run this report, type:"
    MSG_NEW_CONFIG_FILE_EXISTS_ERROR: str = "Config file already exists"
    MSG_NEW_CONFIG_FILE_OVERWRITE: str = (
        "Detected --force, overwriting existing config file"
    )

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

    SCHEMA_EXPORT_FORMATS: list = ["csv", "xlsx"]

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
    MSG_EXPORT_DATABASE_ERROR: str = "There was a problem exporting the database."
    MSG_QUERY_DUPLICATE_ERROR: str = "More than one query has the same name"
    MSG_QUERY_DUPLICATE_ERROR_PS: str = (
        "Please ensure that each query has a unique name, and then try again."
    )
    MSG_VERBOSITY_PS: str = """To debug this problem, you may want to rerun this report
with a higher level of verbosity, such as """

    # import
    MSG_IMPORTING_MODULE_PATH: str = "Importing code from"
    # All import paths are loaded into IMPORT_MODULE_NAME
    IMPORT_MODULE_NAME: str = "yarm_import"
    MSG_POSTPROCESS_FUNCTION_NOT_FOUND: str = "Could not run postprocess function"
    MSG_POSTPROCESS_FUNCTION_NOT_FOUND_PS: str = (
        "Are you sure you defined this function in your import: code?"
    )
    MSG_POSTPROCESS_BUT_NO_IMPORT: str = (
        "No imported code found for postprocess function"
    )
    MSG_POSTPROCESS_BUT_NO_IMPORT_PS: str = (
        "You need to add an import: rule for your code."
    )

    # tables_config
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
    MSG_INCLUDE_INDEX_ALL_TRUE: str = (
        "include_index: Index column included for all tables (unless overridden)."
    )
    MSG_INCLUDE_INDEX_ALL_FALSE: str = (
        "include_index: Index column omitted for all tables (unless overridden)."
    )
    MSG_INCLUDE_INDEX_TABLE_TRUE: str = "include_index: Index column included for table"
    MSG_INCLUDE_INDEX_TABLE_FALSE: str = "include_index: Index column omitted for table"
    MSG_INCLUDE_INDEX_TABLE_PIVOT: str = (
        "include_index: Index column automatically included for pivot table"
    )
    MSG_INCLUDE_INDEX_TABLE_CONFLICT: str = (
        "More than one 'include_index' defined for this table"
    )
    MSG_INCLUDE_INDEX_TABLE_CONFLICT_PS: str = (
        "Please define 'include_index' for only one path, at most, in each table."
    )
    MSG_MERGING_PATH: str = "Merging path"
    MSG_MERGE_ERROR: str = "Merge error: No common column to merge on with table"
    MSG_MERGE_ERROR_PS: str = """Remember: merge column names are...
    - case-sensitive (unless you set lowercase_columns = true)
    - must be spelled the same in every path."""
    MSG_MERGE_TYPE_ERROR: str = "Type error while merging table"
    MSG_CONVERTING_DATETIME: str = "Converting column(s) to datetime:"

    MSG_INPUT_FORMAT_UNRECOGNIZED: str = "Format for input path not recognized"

    MSG_SHOW_DF: str = "Dataframe"
    MSG_NO_SHEET_PROVIDED: str = "No 'sheet' key provided, importing first sheet from"
    MSG_BAD_FILE_EXT: str = "Bad file extension in"
    MSG_CREATE_TABLE_DATABASE_ERROR: str = "Database Error: Could not create table"
    MSG_CREATE_TABLE_VALUE_ERROR: str = "Value Error: Could not create table"
    MSG_MISSING_DATETIME: str = "Column under 'datetime:' not found"
    MSG_PIVOT_FAILED_KEY_ERROR: str = "Pivot failed, because this column is missing"

    # NOTE These keys are for use with Nob objects, not for validating YAML schemas.
    KEY_IMPORT = "/import"
    # within each imported module:
    KEY_MODULE__PATH = "/path"
    KEY_TABLES_CONFIG = "/tables_config"
    # Sheet relative to table
    KEY_TABLE__SHEET = "/sheet"
    KEY_OUTPUT__BASENAME = "/output/basename"
    KEY_OUTPUT__DIR = "/output/dir"
    KEY_INPUT = "/input"
    KEY_INPUT__STRIP = "/input/strip"
    KEY_INPUT__SLUGIFY_COLUMNS = "/input/slugify_columns"
    KEY_INPUT__LOWERCASE_COLUMNS = "/input/lowercase_columns"
    KEY_INPUT__UPPERCASE_ROWS = "/input/uppercase_rows"
    KEY_INPUT__INCLUDE_INDEX = "/input/include_index"
    KEY_OUTPUT__EXPORT_TABLES = "/output/export_tables"
    KEY_OUTPUT__EXPORT_QUERIES = "/output/export_queries"
    KEY_QUERIES = "/queries"

    # tables_config keys. They are deep in the path, so do not use /.
    KEY_PIVOT = "pivot"
    # The schema ensures that each pivot key has one of each of these:
    KEY_PIVOT_INDEX = "index"
    KEY_PIVOT_COLUMNS = "columns"
    KEY_PIVOT_VALUES = "values"

    KEY_DATETIME = "datetime"
    # Individual paths can override the include_index.
    KEY_INCLUDE_INDEX = "include_index"

    # Individual query options
    KEY_QUERY__SQL = "/sql"
    KEY_QUERY__NAME = "/name"
    KEY_QUERY__REPLACE = "/replace"
    KEY_QUERY__POSTPROCESS = "/postprocess"

    CSV = "csv"
    XLSX = "xlsx"

    # export.py
    # Basename for exporting tables
    FILE_EXPORT_TABLES_BASENAME: str = "tables"

    MSG_PROMPT: str = "> "
    MSG_ASK_OVERWRITE_FILE: str = "Overwrite file"
    MSG_REMOVED_FILE: str = "Removed file"
    MSG_REMOVED_FILE_FORCE: str = "Automatic overwrite (--force), removed file"
    MSG_CREATING_DATABASE: str = "Creating database"
    MSG_DATABASE_EXPORTED: str = "Database exported to"
    MSG_OVERWRITE_FILE_ABORT: str = "Cannot proceed without overwriting"

    MSG_EXPORTING_TABLES: str = "Exporting tables to"
    MSG_TABLES_EXPORTED: str = "All tables exported to format"
    MSG_TABLE_EXPORTED: str = "Table exported to"
    MSG_TABLE_EXPORTED_SHEET: str = "Table exported to sheet"
    MSG_QUERIES_EXPORTED: str = "All queries exported to format"
    MSG_QUERY_EXPORTED: str = "Query exported to"
    MSG_QUERY_EXPORTED_SHEET: str = "Query exported to sheet"
    MSG_SHEETS_EXPORTED: str = "All sheets saved in"
    MSG_EXPORT_FORMAT_UNRECOGNIZED: str = "Format for export_tables not recognized"

    MSG_OUTPUT_DIR_EXISTS: str = "Output directory already exists"
    MSG_CREATING_OUTPUT_DIR: str = "Creating output directory"
    MSG_OUTPUT_DIR: str = "Output directory"
    MSG_CANT_CREATE_OUTPUT_DIR: str = "Cannot create output dir at"

    # queries
    MSG_RUNNING_QUERY: str = "Running query"
    MSG_QUERY_RUN_ERROR: str = "Could not run query"
    MSG_APPLYING_REPLACE: str = "Applying replacements to column"
    MSG_QUERY_EMPTY_ERROR: str = "Query returned no results"
    MSG_QUERY_REPLACE_COLUMN_ERROR: str = "Could not find column"
    MSG_QUERY_REPLACE_MATCH_ERROR: str = "Skipping match pattern, could not process"
    MSG_QUERY_REPLACE_ERROR: str = "Could not complete query replacement"
    MSG_APPLYING_POSTPROCESS: str = "Applying postprocess function"
    MSG_POSTPROCESS_NOT_FOUND_ERROR: str = "Could not load postprocess function"
    MSG_POSTPROCESS_OTHER_TYPE_ERROR: str = "Could not apply postprocess function"
    MSG_POSTPROCESS_WRONG_ARGS: str = (
        "Wrong number of arguments in your postprocess function"
    )
    MSG_POSTPROCESS_RETURNED_EMPTY_DF: str = (
        "No data returned from postprocess function"
    )
    MSG_POSTPROCESS_RETURNED_OTHER: str = "Wrong return type from postprocess function"
    MSG_POSTPROCESS_ARGS_PS: str = """Remember:
Your postprocess function must take a DataFrame as its one argument,
and return the processed DataFrame as its one result."""
    MSG_POSTPROCESS_EXAMINE_CODE: str = "This error seems to be in your custom code."
    MSG_QUERY_SAVE_ERROR: str = "Could not save query to database"

    MSG_SUCCESS_REPORT_COMPLETE: str = (
        "Report run complete, output file(s) exported to directory"
    )
