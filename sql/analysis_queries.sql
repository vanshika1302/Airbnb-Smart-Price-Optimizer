-- =============================================================
-- analysis_queries.sql
-- =============================================================
-- Business-facing SQL queries against clean_listings.
-- Plain ANSI SQL -- runs unchanged on DuckDB (this project) or Snowflake.
-- Run with: python etl/run_queries.py

-- Q1. Average and median price by borough, cheapest to most expensive.
-- Business use: where is a host's neighborhood relative to the market?
SELECT
    neighbourhood_group,
    COUNT(*)                                   AS n_listings,
    ROUND(AVG(price), 2)                       AS avg_price,
    ROUND(MEDIAN(price), 2)                    AS median_price,
    ROUND(MIN(price), 2)                       AS min_price,
    ROUND(MAX(price), 2)                       AS max_price
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY neighbourhood_group
ORDER BY avg_price DESC;

-- Q2. Price by room type within each borough.
-- Business use: quantify the "entire home" premium over a private/shared room, by market.
SELECT
    neighbourhood_group,
    room_type,
    COUNT(*)                AS n_listings,
    ROUND(AVG(price), 2)    AS avg_price
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY neighbourhood_group, room_type
ORDER BY neighbourhood_group, avg_price DESC;

-- Q3. Top 15 most expensive neighbourhoods with a meaningful sample size (>= 20 listings).
-- Business use: identify premium micro-markets worth targeted marketing/pricing strategy.
SELECT
    neighbourhood_group,
    neighbourhood,
    COUNT(*)                AS n_listings,
    ROUND(AVG(price), 2)    AS avg_price
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY neighbourhood_group, neighbourhood
HAVING COUNT(*) >= 20
ORDER BY avg_price DESC
LIMIT 15;

-- Q4. Does review activity correlate with availability? (proxy for demand vs. supply)
-- Business use: are highly-reviewed listings kept scarce (lower availability), suggesting pricing power?
SELECT
    availability_bucket,
    COUNT(*)                        AS n_listings,
    ROUND(AVG(number_of_reviews),1) AS avg_reviews,
    ROUND(AVG(price), 2)            AS avg_price
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY availability_bucket
ORDER BY
    CASE availability_bucket
        WHEN 'never_available'    THEN 1
        WHEN 'low_availability'   THEN 2
        WHEN 'medium_availability' THEN 3
        WHEN 'high_availability'  THEN 4
    END;

-- Q5. Portfolio hosts vs. single-listing hosts -- who prices higher?
-- Business use: informs whether "professional" hosts behave differently from casual hosts.
SELECT
    host_size_bucket,
    COUNT(DISTINCT host_id)    AS n_hosts,
    COUNT(*)                   AS n_listings,
    ROUND(AVG(price), 2)       AS avg_price,
    ROUND(AVG(availability_365), 1) AS avg_availability_days
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY host_size_bucket
ORDER BY avg_price DESC;

-- Q6. Minimum-nights policy vs. price -- do longer minimum stays command a discount or premium?
-- Business use: pricing strategy for hosts weighing minimum-night restrictions.
SELECT
    CASE
        WHEN minimum_nights <= 1  THEN '1 night'
        WHEN minimum_nights <= 3  THEN '2-3 nights'
        WHEN minimum_nights <= 7  THEN '4-7 nights'
        WHEN minimum_nights <= 30 THEN '8-30 nights'
        ELSE '30+ nights'
    END AS min_nights_bucket,
    COUNT(*)             AS n_listings,
    ROUND(AVG(price), 2) AS avg_price
FROM clean_listings
WHERE is_price_outlier = FALSE
GROUP BY min_nights_bucket
ORDER BY avg_price DESC;

-- Q7. Listings with zero reviews but priced above their borough's average --
-- candidates for a "may be overpriced / undiscovered" flag (used as a sanity check
-- alongside the model's own flagged listings in the Python layer).
SELECT
    l.id, l.name, l.neighbourhood_group, l.neighbourhood, l.room_type, l.price,
    b.avg_price AS borough_avg_price
FROM clean_listings l
JOIN (
    SELECT neighbourhood_group, AVG(price) AS avg_price
    FROM clean_listings
    WHERE is_price_outlier = FALSE
    GROUP BY neighbourhood_group
) b ON l.neighbourhood_group = b.neighbourhood_group
WHERE l.has_reviews = FALSE
  AND l.is_price_outlier = FALSE
  AND l.price > b.avg_price * 1.5
ORDER BY l.price DESC
LIMIT 20;
