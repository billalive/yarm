"""Run queries on tables."""

import re
import sys
from sqlite3 import Connection

import pandas as pd
from nob.nob import Nob
from nob.nob import NobView
from pandas.core.frame import DataFrame
from pandas.io.sql import DatabaseError

from yarm.export import export_queries
from yarm.helpers import abort
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import show_df
from yarm.helpers import warn
from yarm.settings import Settings


def run_queries(conn: Connection, config: Nob):
    """Run all the queries.

    Args:
        config: Report configuration
        conn: Temporary database in memory

    See Also:
        - :func:`run_query`
        - :func:`save_query_to_database`
        - :func:`yarm.export.export_queries`
    """
    s = Settings()

    if s.KEY_QUERIES in config:
        queries = config[s.KEY_QUERIES]
        df_list = []
        for i, _val in enumerate(queries):
            query = queries[i]
            # Within this query, start keys with "/" to ensure you have correct key.
            # Because "replace" can have arbitrarily named columns, this avoids error
            # if a column is e.g. 'name'.
            sql = query[s.KEY_QUERY__SQL][:]
            name = query[s.KEY_QUERY__NAME][:]

            msg(s.MSG_LINE, verbose=3)
            msg_with_data(s.MSG_RUNNING_QUERY, data=name, verbose=1)
            msg(sql, verbose=3)

            df = run_query(config, query, conn, sql, name)

            # Save processeed query to database.
            save_query_to_database(df, conn, name)

            # Save df to list for export
            # TODO Should this be refactored to avoid the memory usage?
            df_list.append((name, df))

        export_queries(config, df_list)


def query_options(df: DataFrame, config: Nob, query_config: NobView) -> DataFrame:
    """Process options for a particular query.

    Args:
        df: Data with initial query results
        config: Report configuration
        query_config: configuration for this query

    Returns:
        Query data with all options applied for this query.

    See Also:
        - :func:`df_query_replace`
        - :func:`df_query_postprocess`
        - :func:`yarm.validate.validate_key_queries`
    """
    s = Settings()
    qc: NobView = query_config

    show_df(df, qc[s.KEY_QUERY__NAME][:])

    # Process each query option.
    # These options are defined in validate_key_queries()

    df = df_query_replace(df, query_config)

    df = df_query_postprocess(df, config, query_config)

    show_df(df, qc[s.KEY_QUERY__NAME][:])
    return df


def df_query_replace(df: DataFrame, query_config: NobView) -> DataFrame:
    """Process :data:`replace:` keys for a particular query.

    Args:
        df: Query results
        query_config: Configuration for this query

    Returns:
        Query data with replacements applied
    """
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
                    # TODO Can this error ever happen?
                    # except KeyError as error:
                    #    warn(s.MSG_QUERY_REPLACE_ERROR, data=str(error))
                    except re.error as error:
                        warn(
                            s.MSG_QUERY_REPLACE_MATCH_ERROR,
                            data=replace,
                            error=str(error),
                            indent=3,
                        )
            else:
                warn(s.MSG_QUERY_REPLACE_COLUMN_ERROR, data=column_name, indent=1)
    return df


def df_query_postprocess(
    df: DataFrame, config: Nob, query_config: NobView
) -> DataFrame:
    """Process postprocess function for a particular query.

    Args:
        df: Results of query
        config: Report configuration
        query_config: Configuration for this query

    Returns:
        Query data after applying postprocess function

    Important:
        A postprocess function is defined by the user in a separate Python file,
        which must be imported with the :data:`import:` key.
        See :func:`yarm.validate.validate_key_import`
    """
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
        except TypeError as error:  # pragma: no cover
            # TODO This branch is tested in test_query_error(),
            # but coverage misses it.
            error_msg: str = str(error)
            if "positional arguments but 1 was given" in error_msg:
                abort(
                    s.MSG_POSTPROCESS_WRONG_ARGS,
                    data=postprocess,
                    ps=s.MSG_POSTPROCESS_ARGS_PS,
                )
            else:
                abort(
                    s.MSG_POSTPROCESS_OTHER_TYPE_ERROR,
                    data=postprocess,
                    error=error_msg,
                )
        except KeyError as error:
            abort(
                s.MSG_POSTPROCESS_OTHER_TYPE_ERROR,
                data=postprocess,
                error="Key Error: " + str(error),
                suggest_verbose=3,
                ps=s.MSG_POSTPROCESS_EXAMINE_CODE,
            )

        if not isinstance(df, DataFrame):
            abort(
                s.MSG_POSTPROCESS_RETURNED_OTHER,
                data=postprocess,
                ps=s.MSG_POSTPROCESS_ARGS_PS,
            )
        elif df.empty:
            abort(s.MSG_POSTPROCESS_RETURNED_EMPTY_DF, data=postprocess)
    return df


def run_query(config: Nob, query: NobView, conn: Connection, sql: str, name: str):
    """Run a query, apply the options, and return a DataFrame.

    Args:
        config: Report configuration
        query: Configuration for this query
        conn: Temporary database in memory
        sql: SQL statement for this query
        name: Name for this query

    Returns:
        Initial query results

    See Also:
        - :func:`query_options`
    """
    s = Settings()
    try:
        df = pd.read_sql(sql, conn)
        # Empty query results? Sometimes that is desirable, but throw a warning.
        if len(df) == 0:
            warn(s.MSG_QUERY_EMPTY_ERROR, data=name)
        df = query_options(df, config, query)
    except DatabaseError as error:
        abort(s.MSG_QUERY_RUN_ERROR, data=name, error=str(error))
    return df


def save_query_to_database(df: DataFrame, conn: Connection, name: str):
    """Save the processed query to the database.

    Args:
        df: Query data after all processing
        conn: Temporary database in memory
        name: Name for this query
    """
    s = Settings()
    try:
        df.to_sql(name, conn, index=False)
    except DatabaseError as error:  # pragma: no cover
        # TODO Does this error ever trigger?
        abort(s.MSG_QUERY_SAVE_ERROR, data=name, error=str(error))
    except ValueError as error:
        if re.match(r"Table .* already exists", str(error)):
            abort(
                s.MSG_QUERY_DUPLICATE_ERROR,
                data=name,
                ps=s.MSG_QUERY_DUPLICATE_ERROR_PS,
            )
        else:  # pragma: no cover
            # TODO Does this error ever trigger?
            abort(s.MSG_QUERY_SAVE_ERROR, data=name, error=str(error))
        sys.exit()
