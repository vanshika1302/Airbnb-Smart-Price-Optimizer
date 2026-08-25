"""
load.py
-------
LOAD step: write the raw and cleaned data into the warehouse (DuckDB
standing in for Snowflake -- see etl/warehouse.py) so the SQL layer and
the modeling notebook both read from one source of truth instead of
re-parsing CSVs.

Two tables are created:
  * raw_listings       -- untouched extract, for lineage/auditability
  * clean_listings      -- transform() output, what everything else queries
"""

import pandas as pd

from warehouse import get_connection


def load(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> None:
    con = get_connection()

    con.execute("DROP TABLE IF EXISTS raw_listings")
    con.register("raw_df_view", raw_df)
    con.execute("CREATE TABLE raw_listings AS SELECT * FROM raw_df_view")

    con.execute("DROP TABLE IF EXISTS clean_listings")
    con.register("clean_df_view", clean_df)
    con.execute("CREATE TABLE clean_listings AS SELECT * FROM clean_df_view")

    n_raw = con.execute("SELECT COUNT(*) FROM raw_listings").fetchone()[0]
    n_clean = con.execute("SELECT COUNT(*) FROM clean_listings").fetchone()[0]
    print(f"[load] raw_listings: {n_raw:,} rows | clean_listings: {n_clean:,} rows "
          f"-> {get_connection.__module__}")

    con.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform

    raw = extract()
    clean = transform(raw)
    load(raw, clean)
