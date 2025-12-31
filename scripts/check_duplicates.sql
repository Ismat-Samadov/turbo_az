-- ============================================================================
-- Duplicate Detection Queries for Turbo.az Scraper Database
-- ============================================================================
-- Run these queries to monitor data quality and find duplicates
-- ============================================================================

-- Query 1: Check for duplicates by listing_id
-- Expected: 0 rows (listing_id is PRIMARY KEY)
SELECT
    listing_id,
    COUNT(*) as occurrences
FROM scraping.turbo_az
GROUP BY listing_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- Query 2: Check for duplicates by listing_url
-- Expected: 0 rows after adding UNIQUE constraint
SELECT
    listing_url,
    COUNT(*) as occurrences,
    ARRAY_AGG(listing_id) as listing_ids
FROM scraping.turbo_az
GROUP BY listing_url
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- Query 3: Find potential content duplicates
-- (Same car, different listing IDs)
SELECT
    make,
    model,
    year,
    mileage,
    seller_phone,
    COUNT(*) as occurrences,
    ARRAY_AGG(listing_id) as listing_ids,
    ARRAY_AGG(listing_url) as urls
FROM scraping.turbo_az
WHERE make IS NOT NULL AND model IS NOT NULL
GROUP BY make, model, year, mileage, seller_phone
HAVING COUNT(*) > 1
ORDER BY occurrences DESC
LIMIT 20;

-- Query 4: Find same seller with identical cars
-- (Possible duplicates or dealer inventory)
SELECT
    seller_phone,
    make,
    model,
    year,
    COUNT(*) as count,
    ARRAY_AGG(listing_id ORDER BY scraped_at DESC) as listing_ids,
    MIN(scraped_at) as first_seen,
    MAX(scraped_at) as last_seen
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL
GROUP BY seller_phone, make, model, year
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;

-- Query 5: Find listings with very similar titles
-- (Possible duplicates with slight variations)
SELECT
    title,
    COUNT(*) as count,
    ARRAY_AGG(listing_id) as listing_ids
FROM scraping.turbo_az
GROUP BY title
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;

-- Query 6: Use the duplicate_detection view
-- (If created by add_url_uniqueness.py)
SELECT *
FROM scraping.duplicate_detection
ORDER BY occurrences DESC;

-- Query 7: Check data quality - Missing critical fields
SELECT
    'Missing make' as issue,
    COUNT(*) as count
FROM scraping.turbo_az
WHERE make IS NULL OR make = ''

UNION ALL

SELECT
    'Missing model' as issue,
    COUNT(*) as count
FROM scraping.turbo_az
WHERE model IS NULL OR model = ''

UNION ALL

SELECT
    'Missing year' as issue,
    COUNT(*) as count
FROM scraping.turbo_az
WHERE year IS NULL

UNION ALL

SELECT
    'Missing price' as issue,
    COUNT(*) as count
FROM scraping.turbo_az
WHERE price_azn IS NULL OR price_azn = ''

UNION ALL

SELECT
    'Missing seller_phone' as issue,
    COUNT(*) as count
FROM scraping.turbo_az
WHERE seller_phone IS NULL;

-- Query 8: Find suspiciously cheap/expensive listings
-- (Possible data quality issues)
WITH price_stats AS (
    SELECT
        AVG(CAST(REGEXP_REPLACE(price_azn, '[^0-9.]', '', 'g') AS NUMERIC)) as avg_price,
        STDDEV(CAST(REGEXP_REPLACE(price_azn, '[^0-9.]', '', 'g') AS NUMERIC)) as stddev_price
    FROM scraping.turbo_az
    WHERE price_azn ~ '^[0-9,. ₼≈]+$'
)
SELECT
    listing_id,
    listing_url,
    title,
    price_azn,
    make,
    model,
    year
FROM scraping.turbo_az, price_stats
WHERE price_azn ~ '^[0-9,. ₼≈]+$'
AND (
    CAST(REGEXP_REPLACE(price_azn, '[^0-9.]', '', 'g') AS NUMERIC) > (avg_price + 3 * stddev_price)
    OR
    CAST(REGEXP_REPLACE(price_azn, '[^0-9.]', '', 'g') AS NUMERIC) < (avg_price - 3 * stddev_price)
)
ORDER BY price_azn DESC
LIMIT 20;

-- Query 9: Identify stale listings
-- (Not updated in last 30 days)
SELECT
    COUNT(*) as stale_count,
    MIN(scraped_at) as oldest_scrape,
    MAX(scraped_at) as newest_scrape
FROM scraping.turbo_az
WHERE scraped_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Query 10: Database health summary
SELECT
    'Total listings' as metric,
    COUNT(*)::TEXT as value
FROM scraping.turbo_az

UNION ALL

SELECT
    'Unique listing_ids' as metric,
    COUNT(DISTINCT listing_id)::TEXT as value
FROM scraping.turbo_az

UNION ALL

SELECT
    'Unique URLs' as metric,
    COUNT(DISTINCT listing_url)::TEXT as value
FROM scraping.turbo_az

UNION ALL

SELECT
    'Unique sellers' as metric,
    COUNT(DISTINCT seller_phone)::TEXT as value
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL

UNION ALL

SELECT
    'Listings with photos' as metric,
    COUNT(*)::TEXT as value
FROM scraping.turbo_az
WHERE image_urls IS NOT NULL AND image_urls != ''

UNION ALL

SELECT
    'VIP listings' as metric,
    COUNT(*)::TEXT as value
FROM scraping.turbo_az
WHERE is_vip = TRUE

UNION ALL

SELECT
    'Salon listings' as metric,
    COUNT(*)::TEXT as value
FROM scraping.turbo_az
WHERE is_salon = TRUE;

-- ============================================================================
-- CLEANUP QUERIES (USE WITH CAUTION)
-- ============================================================================

-- Cleanup Query 1: Remove exact duplicates by URL (keep most recent)
-- UNCOMMENT TO RUN:
-- WITH duplicates AS (
--     SELECT listing_id,
--            ROW_NUMBER() OVER (
--                PARTITION BY listing_url
--                ORDER BY scraped_at DESC, created_at DESC
--            ) as rn
--     FROM scraping.turbo_az
-- )
-- DELETE FROM scraping.turbo_az
-- WHERE listing_id IN (
--     SELECT listing_id FROM duplicates WHERE rn > 1
-- );

-- Cleanup Query 2: Remove listings with NULL critical fields
-- UNCOMMENT TO RUN:
-- DELETE FROM scraping.turbo_az
-- WHERE make IS NULL
-- OR model IS NULL
-- OR year IS NULL
-- OR listing_url IS NULL;

-- ============================================================================
-- END OF DUPLICATE DETECTION QUERIES
-- ============================================================================
