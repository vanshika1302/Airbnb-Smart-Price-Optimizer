"""
transform.py
------------
TRANSFORM step: clean the raw listings and engineer the features the
pricing model and SQL analysis layer both rely on.

Cleaning decisions (and why):
  * Drop rows with price == 0 -- these are not real bookable prices
    (hosts sometimes zero out a listing to pause it), and they would
    distort both averages and the regression target.
  * Cap price at the 99th percentile before modeling -- a handful of
    listings are listed at $5,000-$10,000/night and are not
    representative; we keep them in the warehouse for transparency but
    flag them so the model isn't dragged around by extreme outliers.
  * Fill missing reviews_per_month with 0 -- a missing value here means
    the listing has zero reviews, not "unknown", which the raw data
    confirms (number_of_reviews == 0 for every row with a null here).
  * Parse last_review to a real date and derive days_since_last_review
    (nulls -> "never reviewed", encoded as -1) so it can be used as a
    numeric feature.
  * Engineer a few business-relevant features: is_entire_home,
    reviews_per_listing_ratio, and a naive host_size_bucket (solo host
    vs. small/large portfolio) since portfolio hosts tend to price
    differently than individual hosts renting a spare room.
"""

import numpy as np
import pandas as pd


PRICE_CAP_PERCENTILE = 0.99


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n_start = len(df)

    # --- basic cleaning -------------------------------------------------
    df = df[df["price"] > 0].copy()

    price_cap = df["price"].quantile(PRICE_CAP_PERCENTILE)
    df["is_price_outlier"] = df["price"] > price_cap

    df["reviews_per_month"] = df["reviews_per_month"].fillna(0.0)

    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    reference_date = pd.Timestamp("2019-07-08")  # ~max date in this snapshot
    df["days_since_last_review"] = (reference_date - df["last_review"]).dt.days
    df["days_since_last_review"] = df["days_since_last_review"].fillna(-1).astype(int)
    df["has_reviews"] = df["number_of_reviews"] > 0

    df["name"] = df["name"].fillna("")
    df["host_name"] = df["host_name"].fillna("Unknown")

    # --- feature engineering ---------------------------------------------
    df["is_entire_home"] = (df["room_type"] == "Entire home/apt").astype(int)

    df["host_size_bucket"] = pd.cut(
        df["calculated_host_listings_count"],
        bins=[0, 1, 5, np.inf],
        labels=["single_listing_host", "small_portfolio_host", "large_portfolio_host"],
    )

    df["availability_bucket"] = pd.cut(
        df["availability_365"],
        bins=[-1, 0, 90, 180, 365],
        labels=["never_available", "low_availability", "medium_availability", "high_availability"],
    )

    df["log_price"] = np.log1p(df["price"])

    keep_cols = [
        "id", "name", "host_id", "host_name",
        "neighbourhood_group", "neighbourhood", "latitude", "longitude",
        "room_type", "is_entire_home",
        "price", "log_price", "is_price_outlier",
        "minimum_nights",
        "number_of_reviews", "has_reviews", "reviews_per_month",
        "last_review", "days_since_last_review",
        "calculated_host_listings_count", "host_size_bucket",
        "availability_365", "availability_bucket",
    ]
    df = df[keep_cols]

    print(f"[transform] {n_start:,} -> {len(df):,} rows after cleaning "
          f"({n_start - len(df):,} dropped for price <= 0)")
    print(f"[transform] price outlier cap (p{int(PRICE_CAP_PERCENTILE*100)}) = ${price_cap:,.0f}, "
          f"{df['is_price_outlier'].sum():,} listings flagged")

    return df


if __name__ == "__main__":
    from extract import extract
    transform(extract())
