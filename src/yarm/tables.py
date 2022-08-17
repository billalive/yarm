"""Create tables."""
import re
from pathlib import Path
from typing import Union

import pandas as pd
from nob.nob import NobView

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
                import_csv(conn, config, table_name, mode, filename)
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
                import_xlsx_sheet(conn, config, table_name, mode, filename, sheet)
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


def import_csv(conn, config, table_name, exists_mode, input_file):
    """Import a CSV file into the database."""
    s = Settings()
    df = pd.read_csv(input_file)
    show_df(df, table_name)
    # TODO
    # df = process_df_import_config(df, config)
    # df = process_df_import_file_options(df, config, table, input_file)
    # index = include_index(config, table, input_file)
    index = False
    try:
        df.to_sql(table_name, conn, if_exists=exists_mode, index=index)
    except pd.io.sql.DatabaseError as error:
        conn.close()
        abort(
            s.MSG_CREATE_TABLE_ERROR, error=error, data=table_name, file_path=input_file
        )


def import_xlsx_sheet(conn, config, table_name, exists_mode, input_file, input_sheet):
    """Import an XLSX sheet into the database."""
    s = Settings()
    with open(input_file, "rb") as f:
        try:
            df = pd.read_excel(f, sheet_name=input_sheet)
            show_df(df, f"{table_name}: {input_sheet}")
        except ValueError as error:
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=error,
                data=table_name,
                file_path=input_file,
            )
        # TODO
        # df = process_df_import_config(df, config)
        # df = process_df_import_file_options(df, config, table, input_file)
        # index = include_index(config, table, input_file)
        index = False
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
