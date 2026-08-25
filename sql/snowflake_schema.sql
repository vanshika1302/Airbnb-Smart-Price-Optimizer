-- =============================================================
-- snowflake_schema.sql
-- =============================================================
-- Target warehouse DDL, written for Snowflake.
--
-- For this mini project, etl/load.py creates the equivalent tables
-- directly in DuckDB (see etl/warehouse.py) so the whole pipeline runs
-- locally with zero cloud setup. This file documents what the SAME
-- schema looks like on Snowflake, so the project is a one-config-change
-- away from running on a real warehouse -- point etl/warehouse.py's
-- get_connection() at Snowflake and run this file once via
-- snowflake-connector-python or the Snowflake CLI.

CREATE DATABASE IF NOT EXISTS AIRBNB_ANALYTICS;
CREATE SCHEMA IF NOT EXISTS AIRBNB_ANALYTICS.PUBLIC;
USE SCHEMA AIRBNB_ANALYTICS.PUBLIC;

CREATE OR REPLACE TABLE raw_listings (
    id                              INTEGER,
    name                            STRING,
    host_id                         INTEGER,
    host_name                       STRING,
    neighbourhood_group             STRING,
    neighbourhood                   STRING,
    latitude                        FLOAT,
    longitude                       FLOAT,
    room_type                       STRING,
    price                           FLOAT,
    minimum_nights                  INTEGER,
    number_of_reviews               INTEGER,
    last_review                     DATE,
    reviews_per_month               FLOAT,
    calculated_host_listings_count  INTEGER,
    availability_365                INTEGER
);

CREATE OR REPLACE TABLE clean_listings (
    id                              INTEGER,
    name                            STRING,
    host_id                         INTEGER,
    host_name                       STRING,
    neighbourhood_group             STRING,
    neighbourhood                   STRING,
    latitude                        FLOAT,
    longitude                       FLOAT,
    room_type                       STRING,
    is_entire_home                  BOOLEAN,
    price                           FLOAT,
    log_price                       FLOAT,
    is_price_outlier                BOOLEAN,
    minimum_nights                  INTEGER,
    number_of_reviews               INTEGER,
    has_reviews                     BOOLEAN,
    reviews_per_month               FLOAT,
    last_review                     DATE,
    days_since_last_review          INTEGER,
    calculated_host_listings_count  INTEGER,
    host_size_bucket                STRING,
    availability_365                INTEGER,
    availability_bucket             STRING
);

-- Loading pattern once this runs on real Snowflake (mini project skips this
-- and loads via pandas -> DuckDB instead, see etl/load.py):
--
-- CREATE OR REPLACE STAGE airbnb_stage;
-- PUT file://data/raw/AB_NYC_2019.csv @airbnb_stage;
-- COPY INTO raw_listings FROM @airbnb_stage/AB_NYC_2019.csv
--   FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');
