"""Run queries."""

import pandas as pd
from nob.nob import Nob
from nob.nob import NobView
from pandas.core.frame import DataFrame
from pandas.io.sql import DatabaseError

from yarm.helpers import abort
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import show_df
from yarm.helpers import warn
from yarm.settings import Settings


def run_queries(conn, config: Nob):
    """Run queries."""
    s = Settings()
    if s.KEY_QUERIES in config:
        queries = config[s.KEY_QUERIES]
        for i, _val in enumerate(queries):
            query = queries[i]
            # Within this query, start keys with "/" to ensure you have correct key.
            # Because "replace" can have arbitrarily named fields, this avoids error
            # if a field is e.g. 'name'.
            sql = query[s.KEY_QUERY__SQL][:]
            name = query[s.KEY_QUERY__NAME][:]

            msg(s.MSG_LINE, verbose=3)
            msg_with_data(s.MSG_RUNNING_QUERY, data=name, verbose=1)
            msg(sql, verbose=3)

            try:
                df = pd.read_sql(sql, conn)
                if len(df) == 0:
                    abort(s.MSG_QUERY_EMPTY_ERROR, data=name)
                df = query_options(df, query)
            except DatabaseError as error:
                abort(s.MSG_QUERY_RUN_ERROR, data=name, error=str(error))


def query_options(df: DataFrame, query_config: NobView):
    """Process options for a particular query.

    Args:
        df (DataFrame): dataframe with initial query results
        query_config (NobView): config for this query

    Returns:
        df (DataFrame):   modified results
    """
    s = Settings()
    qc: NobView = query_config

    show_df(df, qc[s.KEY_QUERY__NAME])

    # Process each query option.
    # These options are defined in validate_key_queries()

    # replace:
    if s.KEY_QUERY__REPLACE in qc:
        for column_name in qc[s.KEY_QUERY__REPLACE][:]:
            if column_name in df.columns:
                msg_with_data(s.MSG_APPLYING_REPLACE, column_name, indent=1)
                column = qc[s.KEY_QUERY__REPLACE][column_name]
                for find in column[:]:
                    try:
                        find = str(find)
                        replace = str(column[find][:])
                        msg_with_data(find, replace, indent=2)
                    except KeyError as error:
                        warn(s.MSG_QUERY_REPLACE_MATCH_ERROR, data=str(error), indent=2)
                    try:
                        df[column_name] = df[column_name].str.replace(
                            find, replace, regex=True
                        )
                    except KeyError as error:
                        warn(s.MSG_QUERY_REPLACE_ERROR, data=str(error))
            else:
                warn(s.MSG_QUERY_REPLACE_COLUMN_ERROR, data=column_name, indent=1)

    # postprocess:
    if s.KEY_QUERY__POSTPROCESS in qc:
        postprocess: str = qc[s.KEY_QUERY__POSTPROCESS][:]
        msg_with_data(
            s.MSG_APPLYING_POSTPROCESS,
            data=postprocess,
            indent=1,
        )

        # cmd: str = f"custom_module.{postprocess}(df)"
        # cmd = getattr(custom, postprocess)
        # eval("print('working:', cmd)")
        # result = cmd(df)

    # if df is None:
    #    abort(f"process_df_function '{key}: {callback}' returned empty dataframe.")

    show_df(df, qc[s.KEY_QUERY__NAME])
    return df
