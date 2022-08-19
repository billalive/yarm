"""Run queries."""

import pandas as pd
from nob.nob import Nob
from pandas.io.sql import DatabaseError

from yarm.helpers import abort
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import show_df
from yarm.settings import Settings


def run_queries(conn, config: Nob):
    """Run queries."""
    s = Settings()
    if s.KEY_QUERIES in config:
        queries = config[s.KEY_QUERIES]
        for i, _val in enumerate(queries):
            query = queries[i]
            sql = query[s.KEY_SQL][:]
            name = query[s.KEY_NAME][:]

            msg(s.MSG_LINE, verbose=3)
            msg_with_data(s.MSG_RUNNING_QUERY, data=name, verbose=1)
            msg(sql, verbose=3)

            try:
                df = pd.read_sql(sql, conn)
                show_df(df, name)
            except DatabaseError as error:
                abort(s.MSG_QUERY_ERROR, data=name, error=str(error))
