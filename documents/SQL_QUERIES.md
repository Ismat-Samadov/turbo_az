# SQL Queries for Turbo.az Database

This document contains useful SQL queries for working with the `scraping.turbo_az` table.

## Table Structure

The data is stored in PostgreSQL with schema `scraping` and table `turbo_az`. Phone numbers are stored as JSONB arrays to handle multiple phones per listing.

## Basic Queries

### 1. Get all listings
```sql
SELECT * FROM scraping.turbo_az
ORDER BY scraped_at DESC
LIMIT 100;
```

### 2. Count total listings
```sql
SELECT COUNT(*) as total_listings
FROM scraping.turbo_az;
```

### 3. Get most recent listings
```sql
SELECT listing_id, title, price_azn, make, model, year, scraped_at
FROM scraping.turbo_az
ORDER BY scraped_at DESC
LIMIT 50;
```

## Phone Number Queries (JSONB)

### 4. Get listings with phone numbers
```sql
SELECT listing_id, title, seller_phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 5. Get listings with multiple phone numbers
```sql
SELECT listing_id, title, seller_phone,
       jsonb_array_length(seller_phone) as phone_count
FROM scraping.turbo_az
WHERE jsonb_array_length(seller_phone) > 1;
```

### 6. Extract first phone number
```sql
SELECT listing_id, title,
       seller_phone->0 as first_phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 7. Extract all phone numbers as separate rows
```sql
SELECT listing_id, title,
       jsonb_array_elements_text(seller_phone) as phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 8. Search for specific phone number
```sql
SELECT listing_id, title, seller_phone
FROM scraping.turbo_az
WHERE seller_phone @> '["994501234567"]'::jsonb;
```

### 9. Count listings by phone number count
```sql
SELECT jsonb_array_length(seller_phone) as phone_count,
       COUNT(*) as listings
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL
GROUP BY jsonb_array_length(seller_phone)
ORDER BY phone_count;
```

## Price Analysis

### 10. Average price by make
```sql
SELECT make,
       COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price,
       MIN(price_azn) as min_price,
       MAX(price_azn) as max_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY make
ORDER BY count DESC
LIMIT 20;
```

### 11. Price distribution by year
```sql
SELECT year,
       COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE year IS NOT NULL AND price_azn > 0
GROUP BY year
ORDER BY year DESC;
```

### 12. Most expensive listings
```sql
SELECT title, make, model, year, price_azn, city
FROM scraping.turbo_az
WHERE price_azn > 0
ORDER BY price_azn DESC
LIMIT 20;
```

## Make and Model Analysis

### 13. Top makes
```sql
SELECT make, COUNT(*) as count
FROM scraping.turbo_az
GROUP BY make
ORDER BY count DESC
LIMIT 20;
```

### 14. Top models by make
```sql
SELECT make, model, COUNT(*) as count
FROM scraping.turbo_az
WHERE make = 'Mercedes'
GROUP BY make, model
ORDER BY count DESC
LIMIT 20;
```

### 15. Popular make/model combinations
```sql
SELECT make, model,
       COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY make, model
HAVING COUNT(*) >= 10
ORDER BY count DESC
LIMIT 30;
```

## Location Analysis

### 16. Listings by city
```sql
SELECT city, COUNT(*) as count
FROM scraping.turbo_az
GROUP BY city
ORDER BY count DESC;
```

### 17. Average price by city
```sql
SELECT city,
       COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY city
HAVING COUNT(*) >= 10
ORDER BY avg_price DESC;
```

## Condition and Features

### 18. Listings by condition
```sql
SELECT condition, COUNT(*) as count
FROM scraping.turbo_az
GROUP BY condition
ORDER BY count DESC;
```

### 19. New vs used listings
```sql
SELECT is_new, COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY is_new;
```

### 20. VIP and featured listings
```sql
SELECT
    COUNT(CASE WHEN is_vip THEN 1 END) as vip_count,
    COUNT(CASE WHEN is_featured THEN 1 END) as featured_count,
    COUNT(CASE WHEN is_salon THEN 1 END) as salon_count,
    COUNT(*) as total
FROM scraping.turbo_az;
```

## Fuel and Transmission

### 21. Listings by fuel type
```sql
SELECT fuel_type, COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY fuel_type
ORDER BY count DESC;
```

### 22. Listings by transmission
```sql
SELECT transmission, COUNT(*) as count,
       ROUND(AVG(price_azn), 2) as avg_price
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY transmission
ORDER BY count DESC;
```

### 23. Electric and hybrid vehicles
```sql
SELECT make, model, year, price_azn, mileage
FROM scraping.turbo_az
WHERE fuel_type IN ('Elektro', 'Hibrid')
ORDER BY year DESC;
```

## Mileage Analysis

### 24. Average mileage by year
```sql
SELECT year,
       COUNT(*) as count,
       ROUND(AVG(mileage), 0) as avg_mileage
FROM scraping.turbo_az
WHERE year IS NOT NULL AND mileage > 0
GROUP BY year
ORDER BY year DESC;
```

### 25. Low mileage listings
```sql
SELECT title, make, model, year, mileage, price_azn
FROM scraping.turbo_az
WHERE mileage > 0 AND mileage < 50000
ORDER BY mileage ASC
LIMIT 50;
```

## Recent Activity

### 26. Recently updated listings
```sql
SELECT listing_id, title, price_azn, updated_date, scraped_at
FROM scraping.turbo_az
WHERE updated_date IS NOT NULL
ORDER BY updated_date DESC
LIMIT 50;
```

### 27. Listings added in last scrape
```sql
SELECT listing_id, title, make, model, year, price_azn
FROM scraping.turbo_az
WHERE scraped_at >= NOW() - INTERVAL '1 day'
ORDER BY scraped_at DESC;
```

## Seller Analysis

### 28. Top sellers by listing count
```sql
SELECT seller_name, COUNT(*) as listing_count,
       COUNT(DISTINCT seller_phone) as unique_phones
FROM scraping.turbo_az
WHERE seller_name IS NOT NULL
GROUP BY seller_name
HAVING COUNT(*) >= 5
ORDER BY listing_count DESC
LIMIT 30;
```

### 29. Listings with credit or barter options
```sql
SELECT
    COUNT(CASE WHEN has_credit THEN 1 END) as with_credit,
    COUNT(CASE WHEN has_barter THEN 1 END) as with_barter,
    COUNT(CASE WHEN has_credit AND has_barter THEN 1 END) as both,
    COUNT(*) as total
FROM scraping.turbo_az;
```

## Advanced Queries

### 30. Find duplicate listings (same make, model, year, price)
```sql
SELECT make, model, year, price_azn, COUNT(*) as duplicates
FROM scraping.turbo_az
WHERE price_azn > 0
GROUP BY make, model, year, price_azn
HAVING COUNT(*) > 1
ORDER BY duplicates DESC;
```

### 31. Price outliers (3 standard deviations from mean)
```sql
WITH price_stats AS (
    SELECT make,
           AVG(price_azn) as avg_price,
           STDDEV(price_azn) as stddev_price
    FROM scraping.turbo_az
    WHERE price_azn > 0
    GROUP BY make
)
SELECT t.listing_id, t.title, t.make, t.model, t.year, t.price_azn,
       ROUND(ps.avg_price, 2) as avg_make_price
FROM scraping.turbo_az t
JOIN price_stats ps ON t.make = ps.make
WHERE t.price_azn > (ps.avg_price + 3 * ps.stddev_price)
   OR t.price_azn < (ps.avg_price - 3 * ps.stddev_price)
ORDER BY t.price_azn DESC;
```

## Useful Tips

1. **JSONB Performance**: The GIN index on `seller_phone` makes JSONB queries fast
2. **Array Operations**: Use `->` for array elements by index (0-based)
3. **Array Search**: Use `@>` operator to check if JSONB array contains a value
4. **Array Length**: Use `jsonb_array_length()` to count elements
5. **Expand Arrays**: Use `jsonb_array_elements_text()` to split arrays into rows

## Export Examples

### Export to CSV
```sql
COPY (
    SELECT listing_id, title, make, model, year, price_azn,
           seller_phone->0 as phone1,
           seller_phone->1 as phone2
    FROM scraping.turbo_az
    WHERE price_azn > 0
    ORDER BY scraped_at DESC
) TO '/tmp/turbo_export.csv' WITH CSV HEADER;
```

### Export specific make to JSON
```sql
COPY (
    SELECT json_agg(t)
    FROM (
        SELECT * FROM scraping.turbo_az
        WHERE make = 'Mercedes'
        LIMIT 100
    ) t
) TO '/tmp/mercedes.json';
```
