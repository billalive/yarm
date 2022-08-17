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
        mode = "replace"

        table: NobView = tables[table_name]

        for i, _val in enumerate(table):
            filename = table[i]["path"][:]
            file_ext = Path(filename).suffix
            msg_with_data(s.MSG_IMPORTING_DATA, filename, verbose=2, indent=1)

            if re.findall("csv", file_ext):
                input_csv(conn, config, table_name, mode, filename)
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
                input_xlsx_sheet(conn, config, table_name, mode, filename, sheet)
            else:
                abort(s.MSG_BAD_FILE_EXT, file_path=filename)
            # If there are any more paths for this table, we will want to append.
            mode = "append"

        msg_with_data(s.MSG_CREATED_TABLE, table_name)


def show_df(df, data: str, verbose: int = 3):
    """Display a dataframe."""
    s = Settings()
    if verbose_ge(verbose):
        print(s.MSG_LINE)
        msg_with_data(s.MSG_SHOW_DF, data=data)
        print(df)
        print(s.MSG_LINE)


def input_csv(conn, config, table_name, exists_mode, input_file):
    """Input a CSV file into the database."""
    s = Settings()
    df = pd.read_csv(input_file)
    show_df(df, table_name)
    df = df_input_options(df, config)
    # FIXME
    # df = df_input_file_options(df, config, table, input_file)
    # index = include_index(config, table, input_file)
    index = False
    try:
        df.to_sql(table_name, conn, if_exists=exists_mode, index=index)
    except pd.io.sql.DatabaseError as error:
        conn.close()
        abort(
            s.MSG_CREATE_TABLE_ERROR, error=error, data=table_name, file_path=input_file
        )


def input_xlsx_sheet(conn, config, table_name, exists_mode, input_file, input_sheet):
    """Input an XLSX sheet into the database."""
    s = Settings()
    with open(input_file, "rb") as f:
        try:
            df = pd.read_excel(f, sheet_name=input_sheet)
            df = df_input_options(df, config)
            # FIXME
            # df = df_input_file_options(df, config, table, input_file)
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

    For per-file input options, see df_table_options.
    """
    s = Settings()
    if s.KEY_INPUT in c:
        # Strip whitespace at start and end of string.
        # https://stackoverflow.com/a/53089888
        # input:
        #   strip: true
        if s.KEY_INPUT__STRIP in c and c[s.KEY_INPUT__STRIP][:]:
            msg("Stripping whitespace at start and end of all strings...")
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

        # index: not processed here, see include_index

    return df
