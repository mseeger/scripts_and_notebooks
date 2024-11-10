import pandas as pd
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine


def run_sql_queries(
    queries: list[str],
    engine: Engine,
) -> list[pd.DataFrame]:
    """
    Runs SQL queries `queries` sequentially, returning the result tables as
    data frames. All queries are run with a connection opened from `engine`
    here. The connection is closed before returning.

    TODO: Deal with errors!

    :param queries: List of SQL queries to execute
    :param engine: Engine to open connections from
    :return: List of result tables
    """
    with engine.connect() as db_conn:
        results = [
            pd.read_sql_query(sql=text(query), con=db_conn)
            for query in queries
        ]
    return results


def run_sql_query(query: str, engine: Engine) -> pd.DataFrame:
    """
    Special case of :func:`run_sql_queries` for a single query. A connection is
    opened and closed for this query.

    :param query: SQL query
    :param engine: Engine to open connections from
    :return: Result table
    """
    return run_sql_queries([query], engine)[0]
