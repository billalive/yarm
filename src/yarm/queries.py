"""Run queries."""

import re
import sys

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

            # Apply query options.
            try:
                df = pd.read_sql(sql, conn)
                # Empty query results? Sometimes that is desirable, but throw a warning.
                if len(df) == 0:
                    warn(s.MSG_QUERY_EMPTY_ERROR, data=name)
                df = query_options(df, config, query)
            except DatabaseError as error:
                abort(s.MSG_QUERY_RUN_ERROR, data=name, error=str(error))

            # Save procesesed query to database.
            try:
                df.to_sql(name, conn, index=False)
            except DatabaseError as error:
                abort(s.MSG_QUERY_SAVE_ERROR, data=name, error=str(error))
            except ValueError as error:
                error = str(error)
                if re.match(r"Table .* already exists", error):
                    abort(
                        s.MSG_QUERY_DUPLICATE_ERROR,
                        data=name,
                        ps=s.MSG_QUERY_DUPLICATE_ERROR_PS,
                    )
                else:
                    abort(s.MSG_QUERY_SAVE_ERROR, data=name, error=str(error))
                sys.exit()

            # FIXME Export query to CSV or XLSX


def query_options(df: DataFrame, config: Nob, query_config: NobView) -> DataFrame:
    """Process options for a particular query.

    Args:
        df (DataFrame): dataframe with initial query results
        config (Nob): config
        query_config (NobView): config for this query

    Returns:
        df (DataFrame):   modified results
    """
    s = Settings()
    qc: NobView = query_config

    show_df(df, qc[s.KEY_QUERY__NAME])

    # Process each query option.
    # These options are defined in validate_key_queries()

    df = df_query_replace(df, query_config)
    df = df_query_postprocess(df, config, query_config)

    show_df(df, qc[s.KEY_QUERY__NAME])
    return df


def df_query_replace(df: DataFrame, query_config: NobView) -> DataFrame:
    """Process replacements for a particular query."""
    s = Settings()
    qc = query_config
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
    return df


def df_query_postprocess(
    df: DataFrame, config: Nob, query_config: NobView
) -> DataFrame:
    """Process postprocess function for a particular query."""
    s = Settings()
    qc = query_config
    # postprocess:
    if s.KEY_QUERY__POSTPROCESS in qc:
        postprocess: str = qc[s.KEY_QUERY__POSTPROCESS][:]
        msg_with_data(
            s.MSG_APPLYING_POSTPROCESS,
            data=postprocess,
            indent=1,
        )

        try:
            module_name = s.IMPORT_MODULE_NAME
            postprocess_function = getattr(sys.modules[module_name], postprocess)
        except AttributeError:
            abort(
                s.MSG_POSTPROCESS_FUNCTION_NOT_FOUND,
                data=postprocess,
                ps=s.MSG_POSTPROCESS_FUNCTION_NOT_FOUND_PS,
            )

        try:
            df = postprocess_function(df)
        except TypeError as error:
            error = str(error)
            if "positional arguments but 1 was given" in error:
                abort(
                    s.MSG_POSTPROCESS_WRONG_ARGS,
                    data=postprocess,
                    ps=s.MSG_POSTPROCESS_ARGS_PS,
                )
            else:
                abort(
                    s.MSG_POSTPROCESS_OTHER_TYPE_ERROR,
                    data=postprocess,
                    error=str(error),
                )
        except KeyError as error:
            abort(
                s.MSG_POSTPROCESS_OTHER_TYPE_ERROR,
                data=postprocess,
                error="KeyError:" + str(error),
                suggest_verbose=3,
                ps=s.MSG_POSTPROCESS_EXAMINE_CODE,
            )

        if df is None:
            abort(
                s.MSG_POSTPROCESS_RETURNED_NONE,
                data=postprocess,
                ps=s.MSG_POSTPROCESS_ARGS_PS,
            )
    return df
