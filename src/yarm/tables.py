"""Create tables."""
import os
import re
from pathlib import Path

import pandas as pd
from nob import Nob
from nob.nob import NobView

from yarm.helpers import abort
from yarm.helpers import msg_with_data
from yarm.settings import Settings
from yarm.validate import check_is_file


def create_tables(conn, config):
    """Import files into database and create tables."""

    s = Settings()

    tables: NobView = config[s.KEY_TABLES_CONFIG]

    for table_name in tables.keys():
        msg_with_data(s.MSG_CREATING_TABLE, table_name)
        print(tables[table_name][:])

        # For each new table, mode should start as "replace"
        mode = "replace"

        table: NobView = tables[table_name]
        print(type(table))

        for i, _val in enumerate(table):
            filename = table[i]["path"][:]
            file_ext = Path(filename).suffix
            msg_with_data(s.MSG_IMPORTING_DATA, filename)

            # f = create_tables[table][filename]

            # indent = "  "
            if re.findall("csv", file_ext):
                # print(indent, "csv")
                import_csv(conn, config, table, mode, filename)
            elif re.findall("xlsx", file_ext):
                # print(indent, "xlsx")
                sheet = get_key_value(table[i], "sheet", None)
                import_xlsx_sheet(conn, config, table, mode, filename, sheet)
            else:
                print(
                    f"ERROR: Unrecognized file extension in",
                    filename,
                    ":",
                    file_ext,
                    "{format(err)}",
                )
                quit()
            # If there are any more files in this table, we will want to append.
            mode = "append"


def import_csv(conn, config, table, exists_mode, input_file):
    """Import a CSV file into the database."""
    df = pd.read_csv(input_file)
    # TODO
    # df = process_df_import_config(df, config)
    # df = process_df_import_file_options(df, config, table, input_file)
    # index = include_index(config, table, input_file)
    index = False
    df.to_sql(table, conn, if_exists=exists_mode, index=index)


def import_xlsx_sheet(conn, config, table, exists_mode, input_file, input_sheet):
    """Import an XLSX sheet into the database."""
    with open(input_file, "rb") as f:
        df = pd.read_excel(f, sheet_name=input_sheet)
        # TODO
        # df = process_df_import_config(df, config)
        # df = process_df_import_file_options(df, config, table, input_file)
        # index = include_index(config, table, input_file)
        index = False
        df.to_sql(table, conn, if_exists=exists_mode, index=index)
