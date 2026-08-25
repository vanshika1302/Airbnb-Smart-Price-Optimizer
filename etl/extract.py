"""
extract.py
----------
EXTRACT step: pull the raw source data into the project untouched.

Source: NYC Airbnb Open Data (2019 snapshot), the standard public dataset
for this type of pricing project -- one listing per row with location,
room type, price, minimum nights, review activity, and availability.

In a production setting this function would hit the Inside Airbnb S3
bucket or a vendor API on a schedule. For this mini project the raw file
already lives in data/raw/AB_NYC_2019.csv, so extract() just validates it
is present and readable, which keeps the ETL boundary explicit even
though there's no network call to make.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "AB_NYC_2019.csv"


def extract() -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw source file not found at {RAW_PATH}. "
            "Place AB_NYC_2019.csv in data/raw/ before running the pipeline."
        )
    df = pd.read_csv(RAW_PATH)
    print(f"[extract] loaded {len(df):,} rows, {df.shape[1]} columns from {RAW_PATH.name}")
    return df


if __name__ == "__main__":
    extract()
