"""
run_pipeline.py
----------------
Orchestrates the full ETL run: extract -> transform -> load.

Usage:
    python etl/run_pipeline.py
"""

from extract import extract
from transform import transform
from load import load


def main():
    print("=" * 60)
    print("Airbnb Smart Price Optimizer -- ETL pipeline")
    print("=" * 60)
    raw_df = extract()
    clean_df = transform(raw_df)
    load(raw_df, clean_df)
    print("=" * 60)
    print("Done. Warehouse ready at data/processed/airbnb_warehouse.duckdb")
    print("=" * 60)


if __name__ == "__main__":
    main()
