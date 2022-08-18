"""Create tables."""
import re
from pathlib import Path
from typing import Union

import pandas as pd
from nob.nob import NobView
from slugify import slugify

from yarm.helpers import abort
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import verbose_ge
from yarm.settings import Settings


def create_tables(conn, config):
    """Import files into database and create tables."""
    s = Settings()

    tables: NobView = config[s.KEY_TABLES_CONFIG]

    for table_name in tables.keys():
        msg(s.MSG_LINE_DOUBLE, verbose=2)
        msg_with_data(s.MSG_CREATING_TABLE, table_name, verbose=2)

        # For each new table, mode should start as "replace"
        exists_mode: str = "replace"

        table: NobView = tables[table_name]

        for i, _val in enumerate(table):
            filename = table[i]["path"][:]
            file_ext = Path(filename).suffix
            msg_with_data(s.MSG_IMPORTING_DATA, filename, verbose=2, indent=1)

            path_config: NobView = table[i]

            if re.findall("csv", file_ext):
                input_csv(
                    conn=conn,
                    config=config,
                    path_config=path_config,
                    table_name=table_name,
                    exists_mode=exists_mode,
                    input_file=filename,
                )
            elif re.findall("xlsx", file_ext):
                sheet = Union[int, str]
                if "sheet" in table[i]:
                    sheet = table[i]["sheet"][:]
                    msg_with_data(s.MSG_IMPORTING_SHEET, sheet, verbose=2, indent=2)
                else:
                    # If no sheet is provided, use the first sheet.
                    # TODO Implement option to import *all* sheets?
                    # pd.read_excel() will do this if sheet_name = None
                    sheet = 0
                    msg_with_data(s.MSG_NO_SHEET_PROVIDED, filename, indent=2)
                input_xlsx_sheet(
                    conn=conn,
                    config=config,
                    path_config=path_config,
                    table_name=table_name,
                    exists_mode=exists_mode,
                    input_file=filename,
                    input_sheet=sheet,
                )
            else:
                abort(s.MSG_BAD_FILE_EXT, file_path=filename)
            # If there are any more paths for this table, we will want to append.
            exists_mode = "append"

        msg_with_data(s.MSG_CREATED_TABLE, table_name)


def show_df(df, data: str, verbose: int = 3):
    """Display a dataframe."""
    s = Settings()
    if verbose_ge(verbose):
        print(s.MSG_LINE)
        msg_with_data(s.MSG_SHOW_DF, data=data)
        print(df)
        print(s.MSG_LINE)


def input_csv(conn, config, table_name, path_config, exists_mode, input_file):
    """Input a CSV file into the database."""
    s = Settings()
    df = pd.read_csv(input_file)
    # Show data before any options (only at high verbosity)
    show_df(df, table_name, 4)
    df = df_input_options(df, config)
    df = df_tables_config_options(df, path_config, table_name, input_file)
    # FIXME
    # index = include_index(config, table, input_file)
    index = False
    try:
        # FIXME Does this merge correctly? If it only merges with the index,
        # then fail if table already exists and index is false.
        df.to_sql(table_name, conn, if_exists=exists_mode, index=index)
        show_df(df, table_name)
    except pd.io.sql.DatabaseError as error:
        conn.close()
        abort(
            s.MSG_CREATE_TABLE_ERROR, error=error, data=table_name, file_path=input_file
        )


def input_xlsx_sheet(
    conn, config, table_name, path_config, exists_mode, input_file, input_sheet
):
    """Input an XLSX sheet into the database."""
    s = Settings()
    with open(input_file, "rb") as f:
        try:
            df = pd.read_excel(f, sheet_name=input_sheet)
            # Show data before any options (only at high verbosity)
            show_df(df, f"{table_name}: {input_sheet}", 4)
            df = df_input_options(df, config)
            df = df_tables_config_options(df, path_config, table_name, input_file)
            # FIXME
            # index = include_index(config, table, input_file)
            index = False
            show_df(df, f"{table_name}: {input_sheet}")
            try:
                df.to_sql(table_name, conn, if_exists=exists_mode, index=index)
            except pd.io.sql.DatabaseError as error:
                conn.close()
                abort(
                    s.MSG_CREATE_TABLE_DATABASE_ERROR,
                    error=error,
                    data=table_name,
                    file_path=input_file,
                )
        except ValueError as error:
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=error,
                data=table_name,
                file_path=input_file,
            )


def df_input_options(df, c):
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
            msg(s.MSG_STRIP_WHITESPACE, verbose=1)
            df = df.applymap(lambda x: x.strip() if type(x) == str else x)

        # input:
        #   slugify_columns: true
        if s.KEY_INPUT__SLUGIFY_COLUMNS in c and c[s.KEY_INPUT__SLUGIFY_COLUMNS][:]:
            msg(s.MSG_SLUGIFY_COLUMNS, verbose=1)
            df.columns = [
                slugify(col, lowercase=False, separator="_") for col in df.columns
            ]

        # input:
        #   lowercase_columns: true
        if s.KEY_INPUT__LOWERCASE_COLUMNS in c and c[s.KEY_INPUT__LOWERCASE_COLUMNS][:]:
            msg(s.MSG_LOWERCASE_COLUMNS, verbose=1)
            df.columns = [col.lower() for col in df.columns]

        # input:
        #   uppercase_rows: true
        # Note: The uppercase transformation happens BEFORE running query, replace
        # This matters for case-sensitive queries and regexes.
        if s.KEY_INPUT__UPPERCASE_ROWS in c and c[s.KEY_INPUT__UPPERCASE_ROWS][:]:
            msg(s.MSG_UPPERCASE_ROWS, verbose=1)
            df = df.applymap(lambda s: s.upper() if type(s) == str else s)

        # TODO Implement option to remove stopwords from column names with slugify?

        # index: not processed here, see include_index

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
            abort(s.MSG_PIVOT_FAILED_KEY_ERROR, data=error, file_path=input_file)
    if s.KEY_DATETIME in pc:
        msg(s.MSG_CONVERTING_DATETIME)
        for key in pc[s.KEY_DATETIME][:]:
            if key in df.columns:
                df = back_up_column(df, key)

                # Make the original column datetime
                df[key] = pd.to_datetime(df[key])

                if pc[s.KEY_DATETIME][key][:] is not None:
                    # If value present, use as datetime format.
                    datetime_format: str = pc[s.KEY_DATETIME][key][:]
                    msg_with_data(f"{s.MSG_TAB}{key}", datetime_format)
                    df[key] = df[key].dt.strftime(f"{datetime_format}")
                else:
                    msg_with_data(f"{s.MSG_TAB}{key}", "(default format)")

            else:
                abort(s.MSG_MISSING_DATETIME, data=key, file_path=input_file)

    # Always return the dataframe!
    return df


def back_up_column(df, col):
    """Save a backup copy of a column."""
    # Make backup copy of this column at column_raw
    col_raw_name: str = f"{col}_raw"
    df[col_raw_name] = df[col]
    col_raw = df.pop(col_raw_name)

    # Move _raw copy to after original column.
    col_index = df.columns.get_loc(col)
    df.insert(col_index + 1, col_raw.name, col_raw)
    return df
