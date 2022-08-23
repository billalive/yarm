"""Export data."""
import os
import sqlite3

# from datetime import date
from typing import List
from typing import Tuple

import pandas as pd
from click import get_current_context
from nob.nob import Nob
from pandas.core.frame import DataFrame

from yarm.helpers import abort
from yarm.helpers import msg_with_data
from yarm.helpers import overwrite_file
from yarm.settings import Settings


def export_database(conn, config: Nob):
    """Export database to sqlite3 database file."""
    s = Settings()
    ctx = get_current_context()
    if ctx.params[s.ARG_EXPORT_DATABASE]:
        export_db: str = get_full_output_basename(config)
        export_db += ".db"

        overwrite_file(export_db)

        msg_with_data(s.MSG_CREATING_DATABASE, export_db, verbose=2)

        try:
            export_conn = sqlite3.connect(export_db)
            for line in conn.iterdump():
                export_conn.execute(line)
        except sqlite3.Error as error:  # pragma: no cover
            abort(s.MSG_EXPORT_DATABASE_ERROR, error=str(error))  # pragma: no cover
        finally:
            export_conn.close()

        msg_with_data(s.MSG_DATABASE_EXPORTED, export_db)


def get_output_dir_path(config: Nob, filename: str):
    """Get full path to filename in output dir."""
    s = Settings()

    output_dir = os.fspath(config[s.KEY_OUTPUT__DIR][:])
    result = os.fspath(f"{output_dir}/{filename}")
    return result


def get_full_output_basename(config: Nob) -> str:
    """Return full basename for output files, with path to output dir."""
    s = Settings()
    basename: str = config[s.KEY_OUTPUT__BASENAME][:]

    # TODO Implement append_date, prepend_date
    # today = date.today()

    path: str = get_output_dir_path(config, basename)

    return path


def export_tables(
    config: Nob,
    conn,
    indent: int = 1,
    verbose: int = 2,
):
    """Export the tables we have created.

    This function expects the connected database to contain
    *only* the tables in the config, *not* the queries yet.
    """
    s = Settings()
    if s.KEY_OUTPUT__EXPORT_TABLES in config:
        # ext should be one of: csv, xlsx, see validate_key_output()
        ext: str = config[s.KEY_OUTPUT__EXPORT_TABLES][:]
        msg_with_data(s.MSG_EXPORTING_TABLES, data=ext, verbose=2)

        export_database_tables(
            config,
            conn,
            ext=ext,
            msg_table_exported_csv=s.MSG_TABLE_EXPORTED,
            msg_table_exported_sheet=s.MSG_TABLE_EXPORTED_SHEET,
            export_basename=s.FILE_EXPORT_TABLES_BASENAME,
            indent=indent,
            verbose=verbose,
        )

        msg_with_data(
            s.MSG_TABLES_EXPORTED,
            data=ext,
            indent=0,
            verbose=1,
        )


def export_database_tables(
    config: Nob,
    conn,
    ext: str,
    msg_table_exported_csv: str,
    msg_table_exported_sheet: str,
    export_basename: str,
    indent: int = 1,
    verbose: int = 2,
):
    """Export all tables in a database as file(s).

    A database "table" may be either one of the tables defined in
    tables_config or one of the queries. Both are saved as database
    "tables".
    """
    s = Settings()
    if ext in s.SCHEMA_EXPORT_FORMATS:
        df_list = []
        # TODO This approach queries the database, rather than our config,
        # for the list of tables. Will this still work after we export queries
        # to the db? Or should queries be saved as Views rather than Tables?
        query: str = "SELECT name from sqlite_master WHERE type ='table'"
        for table in conn.execute(query).fetchall():
            table_name = table[0]
            # NOTE You cannot use placeholders for table names.
            # flake8 flags possible SQL injection here (S608), but we are iterating
            # through table names we just pulled from the database.
            query = "SELECT * from " + table_name  # noqa: S608
            df = pd.read_sql(query, conn, params={"table_name": table_name})
            df_list.append((table_name, df))

        # Export depending on format.
        if ext == "csv":
            for table in df_list:
                table_name = table[0]
                df = table[1]
                export_df_csv(
                    config, df, table_name, msg_table_exported_csv, indent, verbose
                )
        elif ext == "xlsx":  # pragma: no branch
            export_df_list_xlsx(
                config,
                df_list,
                export_basename,
                msg_table_exported_sheet,
                indent,
                verbose,
            )

    else:  # pragma: no cover
        # This path should never execute.
        abort(s.MSG_EXPORT_FORMAT_UNRECOGNIZED, data=ext)  # pragma: no cover


def export_df_csv(
    config: Nob,
    df: DataFrame,
    name: str,
    msg_export: str,
    indent: int = 1,
    verbose: int = 1,
):
    """Export a single dataframe to CSV."""
    ext = "csv"
    filename = get_output_dir_path(config, f"{name}.{ext}")
    overwrite_file(filename)
    df.to_csv(filename, index=False)
    msg_with_data(
        msg_export,
        data=filename,
        indent=indent,
        verbose=verbose,
    )


def export_df_list_xlsx(
    config: Nob,
    df_list: List[Tuple[str, DataFrame]],
    export_basename: str,
    msg_export: str,
    indent: int = 1,
    verbose: int = 1,
):
    """Export a list of dataframes to XLSX.

    Each item in the list should be a tuple:
    (name, df)

    """
    s = Settings()
    ext = "xlsx"
    # NOTE This branch is tested in test_export_tables_xlsx,
    # but coverage does not seem to realize it.
    filename = f"{export_basename}.{ext}"
    filename = get_output_dir_path(config, filename)
    overwrite_file(filename)
    with pd.ExcelWriter(filename) as writer:
        for item in df_list:
            sheet_name = item[0]
            df = item[1]
            # TODO Are there any situations where our spreadsheet needs the index?
            # Probably not.
            # If a table is imported into the database with include_index = True,
            # then when it is later exported, the index is simply another column.
            index = False
            df.to_excel(writer, sheet_name=sheet_name, index=index)
            msg_with_data(
                msg_export,
                data=sheet_name,
                indent=indent,
                verbose=verbose,
            )
    msg_with_data(
        s.MSG_SHEETS_EXPORTED,
        data=filename,
        indent=indent,
        verbose=verbose,
    )


def export_queries(config, df_list):
    """Export queries."""
    s = Settings()
    # Export queries to CSV or XLSX
    # By default, queries export to xlsx.
    ext = s.XLSX
    # Override if needed.
    if s.KEY_OUTPUT__EXPORT_QUERIES in config:
        ext = config[s.KEY_OUTPUT__EXPORT_QUERIES][:]

    if ext in s.SCHEMA_EXPORT_FORMATS:
        indent = 1
        verbose = 2
        if ext == "csv":
            for table in df_list:
                table_name = table[0]
                df = table[1]
                export_df_csv(
                    config,
                    df,
                    table_name,
                    s.MSG_QUERY_EXPORTED,
                    indent=indent,
                    verbose=verbose,
                )
        elif ext == "xlsx":  # pragma: no branch
            export_df_list_xlsx(
                config,
                df_list,
                config[s.KEY_OUTPUT__BASENAME],
                s.MSG_QUERY_EXPORTED_SHEET,
                indent=indent,
                verbose=verbose,
            )
    else:  # pragma: no cover
        # This path should never execute.
        abort(s.MSG_EXPORT_FORMAT_UNRECOGNIZED, data=ext)  # pragma: no cover
