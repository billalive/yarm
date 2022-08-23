"""Export data."""
import os
import sqlite3
from datetime import date

import pandas as pd
from click import get_current_context
from nob.nob import Nob

from yarm.helpers import abort
from yarm.helpers import msg_with_data
from yarm.helpers import overwrite_file
from yarm.settings import Settings


# from pandas.core.frame import DataFrame


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
    today = date.today()
    print(today)

    path: str = get_output_dir_path(config, basename)

    return path


def export_tables(
    config: Nob,
    conn,
    indent: int = 1,
    verbose: int = 2,
):
    """Export a table to a file."""
    s = Settings()
    if s.KEY_OUTPUT__EXPORT_TABLES in config:
        # ext should be one of: csv, xlsx, see validate_key_output()
        ext: str = config[s.KEY_OUTPUT__EXPORT_TABLES][:]
        msg_with_data(s.MSG_EXPORTING_TABLES, data=ext, verbose=2)
        if ext in s.SCHEMA_EXPORT_FORMATS:
            df_tables = []
            # TODO This approach queries the database, rather than our config,
            # the list of tables. Will this still work after we export queries
            # to the db? Or should queries be saved as Views rather than Tables?
            query: str = "SELECT name from sqlite_master WHERE type ='table'"
            for table in conn.execute(query).fetchall():
                table_name = table[0]
                # NOTE You cannot use placeholders for table names.
                # flake8 flags possible SQL injection here (S608), but we are iterating
                # through table names we just pulled from the database.
                query = "SELECT * from " + table_name  # noqa: S608
                df = pd.read_sql(query, conn, params={"table_name": table_name})
                df_tables.append((table_name, df))

            # Export depending on format.
            if ext == "csv":
                for table in df_tables:
                    table_name = table[0]
                    df = table[1]
                    filename = get_output_dir_path(config, f"{table_name}.{ext}")
                    overwrite_file(filename)
                    df.to_csv(filename, index=False)
                    msg_with_data(
                        s.MSG_TABLE_EXPORTED,
                        data=filename,
                        indent=indent,
                        verbose=verbose,
                    )
            elif ext == "xlsx":  # pragma: no branch
                # NOTE This branch is tested in test_export_tables_xlsx
                # but coverage does not seem to realize it.
                filename = f"{s.FILE_EXPORT_TABLES_BASENAME}.{ext}"
                filename = get_output_dir_path(config, filename)
                overwrite_file(filename)
                with pd.ExcelWriter(filename) as writer:
                    for table in df_tables:
                        table_name = table[0]
                        df = table[1]
                        df.to_excel(writer, sheet_name=table_name)

        else:  # pragma: no cover
            # This path should never execute.
            abort(s.MSG_EXPORT_FORMAT_UNRECOGNIZED, data=ext)  # pragma: no cover

        msg_with_data(
            s.MSG_TABLES_EXPORTED,
            data=ext,
            indent=0,
            verbose=1,
        )
