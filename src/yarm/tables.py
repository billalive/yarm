"""Create tables."""
import re
from pathlib import Path
from typing import Union

import pandas as pd
from nob.nob import Nob
from nob.nob import NobView
from pandas.core.frame import DataFrame
from slugify import slugify

from yarm.export import export_tables
from yarm.helpers import abort
from yarm.helpers import key_show_message
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import show_df
from yarm.settings import Settings


def create_tables(conn, config):
    """Import files into database and create tables."""
    s = Settings()

    tables: NobView = config[s.KEY_TABLES_CONFIG]

    include_index_all: bool = get_include_index_all(config)

    # Input options apply to all tables, so show them once here.
    key_msg: list = [
        (s.KEY_INPUT__STRIP, s.MSG_STRIP_WHITESPACE),
        (s.KEY_INPUT__SLUGIFY_COLUMNS, s.MSG_SLUGIFY_COLUMNS),
        (s.KEY_INPUT__LOWERCASE_COLUMNS, s.MSG_LOWERCASE_COLUMNS),
        (s.KEY_INPUT__UPPERCASE_ROWS, s.MSG_UPPERCASE_ROWS),
    ]
    key_show_message(key_msg, config, verbose=1)

    for table_name in tables.keys():
        msg(s.MSG_LINE_DOUBLE, verbose=2)
        msg_with_data(s.MSG_CREATING_TABLE, table_name, verbose=2)

        # For each new table, mode should start as "replace"
        exists_mode: str = "replace"

        table: NobView = tables[table_name]
        table_df = None

        include_index_table: bool = get_include_index_table(
            table, table_name, include_index_all
        )

        for i, _val in enumerate(table):
            filename = table[i]["path"][:]
            file_ext = Path(filename).suffix
            msg_with_data(s.MSG_IMPORTING_DATA, filename, verbose=2, indent=1)

            path_config: NobView = table[i]

            if re.findall(s.CSV, file_ext):
                table_df = input_path(
                    input_format=s.CSV,
                    conn=conn,
                    config=config,
                    path_config=path_config,
                    table_name=table_name,
                    table_df=table_df,
                    input_file=filename,
                    input_sheet=None,
                )
            elif re.findall(s.XLSX, file_ext):
                sheet = Union[int, str]
                if s.KEY_SHEET in table[i]:
                    sheet = table[i][s.KEY_SHEET][:]
                    msg_with_data(s.MSG_IMPORTING_SHEET, sheet, verbose=2, indent=2)
                else:
                    # If no sheet is provided, use the first sheet.
                    # TODO Implement option to import *all* sheets?
                    # pd.read_excel() will do this if sheet_name = None
                    # TODO Implement option to pass a sheet number instead of name?
                    sheet = 0
                    msg_with_data(s.MSG_NO_SHEET_PROVIDED, filename, indent=2)
                table_df = input_path(
                    input_format=s.XLSX,
                    conn=conn,
                    config=config,
                    path_config=path_config,
                    table_name=table_name,
                    table_df=table_df,
                    input_file=filename,
                    input_sheet=sheet,
                )
            else:
                abort(s.MSG_BAD_FILE_EXT, file_path=filename)
            # If there are any more paths for this table, we will want to append.
            exists_mode = "append"

        try:
            table_df.to_sql(
                table_name, conn, if_exists=exists_mode, index=include_index_table
            )
            msg_with_data(s.MSG_CREATED_TABLE, table_name)
        except pd.io.sql.DatabaseError as error:  # pragma: no cover
            # TODO Figure out how to test these errors.
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_DATABASE_ERROR,
                error=error,
                data=table_name,
            )
        except ValueError as error:  # pragma: no cover
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=error,
                data=table_name,
            )
    export_tables(config=config, conn=conn)


def get_include_index_all(config: Nob) -> bool:
    """Set input:include_index for all inputs."""
    s = Settings()
    include_index_all: bool = False
    if s.KEY_INPUT__INCLUDE_INDEX in config:
        include_index_all = config[s.KEY_INPUT__INCLUDE_INDEX][:]
    if include_index_all:
        msg(s.MSG_INCLUDE_INDEX_ALL_TRUE, verbose=2)
    else:
        msg(s.MSG_INCLUDE_INDEX_ALL_FALSE, verbose=2)
    return include_index_all


def get_include_index_table(
    table: NobView, table_name: str, include_index_all: bool
) -> bool:
    """Set include_index for a particular table."""
    s = Settings()
    include_index_table: bool = include_index_all

    msg: Union[str, None] = None

    # Special case: by default, a pivot table loses its index, which is
    # confusing. Set this to true now, so that user can override below.
    if s.KEY_PIVOT in table:
        include_index_table = True
        msg = s.MSG_INCLUDE_INDEX_TABLE_PIVOT

    # NOTE We have already confirmed that only one include_index, at most,
    # is in this table. See validate_key_tables_config()
    if s.KEY_INCLUDE_INDEX in table:
        include_index_table = table[s.KEY_INCLUDE_INDEX][:]
        if table[s.KEY_INCLUDE_INDEX][:]:
            msg = s.MSG_INCLUDE_INDEX_TABLE_TRUE
        else:
            msg = s.MSG_INCLUDE_INDEX_TABLE_FALSE

    if msg:
        msg_with_data(msg, data=table_name, verbose=2, indent=1)

    return include_index_table


def input_path(
    input_format: str,
    conn,
    config: Nob,
    path_config: NobView,
    table_name: str,
    table_df: Union[DataFrame, None],
    input_file: str,
    input_sheet: Union[int, str, None],
) -> DataFrame:
    """Input a path into a table DataFrame.

    If we have already imported at least one path into this table,
    pass this table as table_df, and merge in this new path.

    If this is the first path for this table, table_df should be None.
    """
    s = Settings()

    msg_show_df: str = table_name

    if input_format == s.CSV:
        df: DataFrame = pd.read_csv(input_file)
    elif input_format == s.XLSX:
        msg_show_df += f": {input_sheet}"
        with open(input_file, "rb") as f:
            df = pd.read_excel(f, sheet_name=input_sheet)
    else:  # pragma: no cover
        # This branch should never execute, because of previous tests.
        abort(s.MSG_INPUT_FORMAT_UNRECOGNIZED, data=input_format)

    # Show data before any options (only at high verbosity)
    show_df(df, msg_show_df, 4)

    df = df_input_options(df, config)
    df = df_tables_config_options(df, path_config, table_name, input_file)

    # After all transformations, merge to existing table_df.
    msg_with_data(s.MSG_MERGING_PATH, data=input_file, indent=1, verbose=2)
    if isinstance(table_df, DataFrame):
        try:
            df = pd.merge(left=table_df, right=df, how="outer")
        except pd.errors.MergeError:
            abort(
                s.MSG_MERGE_ERROR,
                data=table_name,
                file_path=input_file,
                ps=s.MSG_MERGE_ERROR_PS,
            )
        except TypeError as error:  # pragma: no cover
            # TODO Figure out how to test this.
            abort(
                s.MSG_MERGE_TYPE_ERROR,
                error=str(error),
                data=table_name,
                file_path=input_file,
            )
        except ValueError as error:
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=str(error),
                data=table_name,
            )
    show_df(df, table_name)
    return df


def df_input_options(df: DataFrame, c):
    """Process input data using the options in input: key.

    These options are applied to /every/ input file.

    If you modify these options, you must also modify validate_key_input()

    For per-file options, see df_tables_config_options().
    """
    s = Settings()
    if s.KEY_INPUT in c:
        # Strip whitespace at start and end of string.
        # https://stackoverflow.com/a/53089888
        # input:
        #   strip: true
        if s.KEY_INPUT__STRIP in c and c[s.KEY_INPUT__STRIP][:]:
            df = df.applymap(lambda x: x.strip() if type(x) == str else x)

        # input:
        #   slugify_columns: true
        if s.KEY_INPUT__SLUGIFY_COLUMNS in c and c[s.KEY_INPUT__SLUGIFY_COLUMNS][:]:
            df.columns = [
                slugify(col, lowercase=False, separator="_") for col in df.columns
            ]

        # input:
        #   lowercase_columns: true
        if s.KEY_INPUT__LOWERCASE_COLUMNS in c and c[s.KEY_INPUT__LOWERCASE_COLUMNS][:]:
            df.columns = [col.lower() for col in df.columns]

        # input:
        #   uppercase_rows: true
        # Note: The uppercase transformation happens BEFORE running query, replace
        # This matters for case-sensitive queries and regexes.
        if s.KEY_INPUT__UPPERCASE_ROWS in c and c[s.KEY_INPUT__UPPERCASE_ROWS][:]:
            df = df.applymap(lambda s: s.upper() if type(s) == str else s)

        # TODO Implement option to remove stopwords from column names with slugify?

        # include_index: not processed here, see create_tables()

    return df


def df_tables_config_options(df, path_config: NobView, table_name: str, input_file):
    """Process tables_config: options for a particular path.

    For input: options applied to all input files, see df_input_options().

    A table is defined as a list of one or more paths, all of which are merged into
    a single table. So we can only process options for one path at a time.

    If you modify these path options, you must also modify validate_key_tables_config().

    That function also ensures that all necessary keys are present (e.g., that if
    a pivot stanza is present, it also has index, columns, and values).

    Args:
        df: dataframe containing this table.
            May have data from previously imported paths.
        path_config: config for this path only.
        table_name: name of this table.
        input_file: path to this data.

    Returns:
        df: dataframe of this table, with options applied from this path.
    """
    s = Settings()
    pc: NobView = path_config
    if s.KEY_PIVOT in pc:
        msg_with_data(s.MSG_APPLYING_PIVOT, input_file)
        # show_df(df, table_name, 4)
        try:
            df = pd.pivot(
                data=df,
                index=pc[s.KEY_PIVOT_INDEX][:],
                columns=pc[s.KEY_PIVOT_COLUMNS][:],
                values=pc[s.KEY_PIVOT_VALUES][:],
            )
        except KeyError as error:
            abort(s.MSG_PIVOT_FAILED_KEY_ERROR, data=str(error), file_path=input_file)
    if s.KEY_DATETIME in pc:
        msg(s.MSG_CONVERTING_DATETIME, indent=1, verbose=2)
        for key in pc[s.KEY_DATETIME][:]:
            if key in df.columns:
                df = back_up_column(df, key)

                # Make the original column datetime
                df[key] = pd.to_datetime(df[key])

                if pc[s.KEY_DATETIME][key][:] is not None:
                    # If value present, use as datetime format.
                    # TODO Test for bad format? strictyaml makes this a str,
                    # so it may not be possible to trigger an error.
                    datetime_format: str = pc[s.KEY_DATETIME][key][:]
                    msg_with_data(key, data=datetime_format, indent=2, verbose=2)
                    df[key] = df[key].dt.strftime(f"{datetime_format}")
                else:
                    msg_with_data(key, data="(default format)", indent=2, verbose=2)

            else:
                abort(s.MSG_MISSING_DATETIME, data=key, file_path=input_file)

    # Always return the dataframe!
    return df


def back_up_column(df: DataFrame, col):
    """Save a backup copy of a column."""
    # Make backup copy of this column at column_raw
    col_raw_name: str = f"{col}_raw"
    df[col_raw_name] = df[col]
    col_raw = df.pop(col_raw_name)

    # Move _raw copy to after original column.
    col_index = df.columns.get_loc(col)
    df.insert(col_index + 1, col_raw.name, col_raw)
    return df
