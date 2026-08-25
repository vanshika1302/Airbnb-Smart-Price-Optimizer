# Airbnb Smart Price Optimizer

**[View the live case study →](https://vanshika1302.github.io/Airbnb-Smart-Price-Optimizer/)**
An interactive one-page walkthrough of this project's findings, model comparison, and a live
price-lookup tool, hosted directly from this repo via GitHub Pages. (Source: `index.html`.)

A mini business-analytics project: given a listing's location, room type, host profile, and
review activity, recommend a reasonable nightly price and flag listings that look meaningfully
over- or under-priced relative to comparable listings.

Built as a portfolio project for the UCSD MSBA program, scoped to exercise Python, SQL, ETL, and
data-warehouse fundamentals end to end on a real (if imperfect) dataset — not just a notebook with
a `pd.read_csv()` at the top.

## Business problem

Hosts on platforms like Airbnb set prices largely by intuition or by copying nearby listings.
That leaves money on the table in both directions: underpriced listings lose revenue on every
booked night, and overpriced listings sit vacant. This project builds a data-driven pricing
reference point — "what does a listing like this typically go for?" — that a host or a platform's
pricing team could use as a sanity check against their own listing.

## Data

**Source:** [NYC Airbnb Open Data](https://raw.githubusercontent.com/rajtulluri/Airbnb-Data-Exploratory-Analysis/master/AB_NYC_2019.csv)
(2019 snapshot), the standard public dataset for this class of pricing project — ~48,900 listings
with location, room type, price, minimum-night policy, review activity, and availability.

**Note on scope:** I originally planned to pull a live snapshot from Inside Airbnb for a specific
city (San Diego), but Inside Airbnb's data bucket wasn't reachable from this build environment.
I used the well-established NYC 2019 dataset instead — it's the most widely benchmarked dataset for
this exact problem, which makes it easy to sanity-check results against published work, at the
cost of being slightly dated and lacking bedroom/bathroom/amenity counts that a full Inside Airbnb
detailed export would include. See **Limitations** below.

## Architecture

```
data/raw/AB_NYC_2019.csv
        |
        v
   etl/extract.py    -->  validate & load raw CSV
        |
        v
   etl/transform.py  -->  clean nulls, cap outliers, engineer features
        |
        v
   etl/load.py        -->  write raw_listings + clean_listings tables
        |
        v
  DuckDB warehouse (data/processed/airbnb_warehouse.duckdb)
        |                                   |
        v                                   v
  sql/analysis_queries.sql          notebooks/eda_and_modeling.ipynb
  (business SQL, run via                (EDA + Linear Regression +
   etl/run_queries.py)                   Random Forest + price flags)
```

The warehouse layer is DuckDB, not Snowflake, on purpose — it needs zero setup or credentials,
which matters for a class project that has to run on any grader's machine. `etl/warehouse.py`
isolates the connection behind one function, and `sql/snowflake_schema.sql` documents the
equivalent Snowflake DDL and load pattern, so pointing this at a real Snowflake account later is a
config change, not a rewrite. All SQL in `sql/` is plain ANSI SQL for that reason.

## Tech stack

Python (pandas, scikit-learn), SQL, DuckDB (Snowflake-compatible SQL surface), Jupyter.

## Repository structure

```
dashboard.html                  live case-study page (source for the hosted link above)
data/
  raw/AB_NYC_2019.csv          source extract
  processed/                    warehouse + saved query results (generated)
etl/
  extract.py, transform.py, load.py, run_pipeline.py, run_queries.py, warehouse.py
sql/
  snowflake_schema.sql          target warehouse DDL (Snowflake)
  analysis_queries.sql          7 business questions in SQL
notebooks/
  eda_and_modeling.ipynb        EDA, modeling, price-flagging (fully executed with outputs)
models/
  price_model_random_forest.joblib, model_feature_columns.joblib, model_comparison.csv
```

## How to run

```bash
pip install -r requirements.txt

# 1. Run the ETL pipeline: extract -> clean -> load into the warehouse
python etl/run_pipeline.py

# 2. Run the SQL business-question layer (prints + saves results as CSV)
python etl/run_queries.py

# 3. Open the notebook for EDA, modeling, and price recommendations
jupyter notebook notebooks/eda_and_modeling.ipynb
```

## Key findings

**From SQL (`sql/analysis_queries.sql`):**

| Borough | Avg. price | Median price |
|---|---|---|
| Manhattan | $172.90 | $149 |
| Brooklyn | $115.92 | $90 |
| Staten Island | $94.24 | $75 |
| Queens | $94.10 | $75 |
| Bronx | $83.86 | $65 |

Manhattan commands roughly a 50% premium over Brooklyn and more than double the Bronx. Within
every borough, an entire home/apartment rents for 2-3x a private or shared room. Portfolio hosts
(5+ listings) price about 12% higher than single-listing hosts and keep listings available far
more days per year (255 vs. 78) — consistent with professional hosts optimizing occupancy rather
than renting out a spare room occasionally.

**From modeling (`notebooks/eda_and_modeling.ipynb`):**

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | $48.08 | $83.85 | 0.354 |
| Random Forest | $42.31 | $73.88 | 0.498 |

The Random Forest explains about half the variance in price using only location, room type,
minimum-night policy, review activity, and host portfolio size — and clearly beats the linear
baseline, confirming price is driven by interactions (e.g. "entire home *in Manhattan*") rather
than additive effects. Location and room type dominate feature importance.

Using the model as a reference price, the notebook flags listings priced 40%+ above or below what
comparable listings command — a concrete, actionable list a pricing or host-support team could
review directly (see notebook section 5).

## Limitations & next steps

- **Feature richness:** this snapshot doesn't include bedrooms, bathrooms, amenities, or photos,
  which a production pricing model would use. The ETL/SQL/modeling structure here is built so a
  full Inside Airbnb "detailed listings" export (79 columns) could be substituted in `data/raw/`
  with only `etl/transform.py`'s feature list needing an update.
- **Snowflake:** the warehouse layer runs on DuckDB for zero-setup reproducibility; `sql/snowflake_schema.sql`
  documents the drop-in Snowflake schema for when real warehouse credentials are available.
- **Recency:** the data is a 2019 snapshot; a refreshed pull would better reflect current pricing.
- **Model:** a gradient-boosted model (XGBoost/LightGBM) would likely edge out the Random Forest
  and is a natural next iteration once the feature set is richer.
