"""
warehouse.py
------------
Thin connection layer for the project's analytics warehouse.

For this mini project we run everything locally against DuckDB, which
speaks (almost) the same SQL dialect as Snowflake and needs zero setup or
credentials -- perfect for a class project you need to hand in and demo
on any machine.

Everything downstream (etl/load.py, sql/*.sql, notebooks) talks to the
warehouse ONLY through get_connection(), so swapping DuckDB for a real
Snowflake account later is a one-function change, not a rewrite:

    def get_connection():
        import snowflake.connector
        return snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema=os.environ["SNOWFLAKE_SCHEMA"],
        )

The SQL in sql/ is written in plain ANSI SQL on purpose (no DuckDB-only
functions) so it runs unchanged on Snowflake.
"""

from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "airbnb_warehouse.duckdb"


def get_connection():
    """Return a connection to the local warehouse (DuckDB stand-in for Snowflake)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def run_sql_file(con, path):
    """Execute a .sql file that may contain multiple ';'-separated statements."""
    sql_text = Path(path).read_text()
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    results = []
    for stmt in statements:
        results.append(con.execute(stmt))
    return results
