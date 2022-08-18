"""Export data."""
import os
import sqlite3
from datetime import date

from click import get_current_context
from nob.nob import Nob

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
        except sqlite3.Error as error:
            abort(s.MSG_SQLITE_ERROR, error=error)
        finally:
            export_conn.close()

        msg_with_data(s.MSG_DATABASE_EXPORTED, export_db)


def get_output_dir_path(config: Nob, filename: str):
    """Get full path to filename in output dir."""
    s = Settings()

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
