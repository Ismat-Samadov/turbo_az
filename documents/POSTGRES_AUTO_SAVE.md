# PostgreSQL Auto-Save Feature

The turbo.az scraper automatically saves all scraped data directly to PostgreSQL database. This document explains how the auto-save feature works.

## Overview

- **No CSV files**: The scraper no longer creates CSV files
- **Direct database saving**: All data goes directly to PostgreSQL
- **Upsert logic**: Duplicate listings are automatically updated instead of causing errors
- **JSONB phone storage**: Multiple phone numbers are stored as JSON arrays
- **Batch processing**: Uses batch inserts for better performance

## How It Works

### 1. Database Connection

The scraper reads the `DATABASE_URL` from environment variables:

```python
DATABASE_URL = os.getenv('DATABASE_URL')
# Format: postgresql://user:password@host/database?sslmode=require
```

### 2. Phone Number Processing

Phone numbers are converted from pipe-separated strings to JSONB arrays:

```python
def parse_phone_numbers(phone_str):
    """Convert phone string to JSON array"""
    if not phone_str or phone_str == '':
        return None
    phones = [p.strip() for p in str(phone_str).split('|') if p.strip()]
    return json.dumps(phones) if phones else None
```

**Examples**:
- Single phone: `"994501234567"` → `["994501234567"]`
- Multiple phones: `"994501234567|994551234567"` → `["994501234567", "994551234567"]`
- Empty: `""` → `NULL`

### 3. Upsert Logic (Insert or Update)

The scraper uses `ON CONFLICT DO UPDATE` to prevent duplicate errors:

```sql
INSERT INTO scraping.turbo_az (
    listing_id, listing_url, title, price_azn, ...
) VALUES (%s, %s, %s, %s, ...)
ON CONFLICT (listing_id) DO UPDATE SET
    listing_url = EXCLUDED.listing_url,
    title = EXCLUDED.title,
    price_azn = EXCLUDED.price_azn,
    ...
```

**What this means**:
- If `listing_id` doesn't exist → Insert new row
- If `listing_id` already exists → Update all fields with new values
- No errors, no duplicates, always latest data

### 4. Batch Processing

Data is inserted in batches of 100 for better performance:

```python
from psycopg2.extras import execute_batch

execute_batch(cursor, insert_sql, batch, page_size=100)
```

### 5. Save Method

The `save_to_postgres()` method is called automatically at the end of scraping:

```python
def save_to_postgres(self):
    """Save scraped data to PostgreSQL database"""
    if not self.scraped_listings:
        logger.warning("No listings to save to PostgreSQL")
        return

    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables")
        return

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Prepare data with phone parsing
        data_to_insert = []
        for listing in self.scraped_listings:
            # Convert phone numbers to JSONB
            phone_json = parse_phone_numbers(listing.get('seller_phone', ''))

            # Prepare tuple for insertion
            data_to_insert.append((
                listing.get('listing_id'),
                listing.get('listing_url'),
                listing.get('title'),
                # ... all other fields ...
                phone_json,
                datetime.now()  # scraped_at
            ))

        # Batch insert with upsert
        execute_batch(cursor, insert_sql, data_to_insert, page_size=100)

        conn.commit()
        logger.info(f"✓ Saved {len(data_to_insert)} listings to PostgreSQL")

    except Exception as e:
        logger.error(f"Failed to save to PostgreSQL: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
```

## Database Schema

```sql
CREATE TABLE scraping.turbo_az (
    listing_id BIGINT PRIMARY KEY,
    listing_url TEXT,
    title TEXT,
    price_azn NUMERIC(12,2),
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    mileage INTEGER,
    engine_volume NUMERIC(4,1),
    engine_power INTEGER,
    fuel_type VARCHAR(50),
    transmission VARCHAR(50),
    drivetrain VARCHAR(50),
    body_type VARCHAR(50),
    color VARCHAR(50),
    seats_count INTEGER,
    condition VARCHAR(50),
    market VARCHAR(100),
    is_new BOOLEAN,
    city VARCHAR(100),
    seller_name VARCHAR(255),
    seller_phone JSONB,  -- Stores phone arrays
    description TEXT,
    extras TEXT,
    views INTEGER,
    updated_date TIMESTAMP,
    posted_date TIMESTAMP,
    is_vip BOOLEAN,
    is_featured BOOLEAN,
    is_salon BOOLEAN,
    has_credit BOOLEAN,
    has_barter BOOLEAN,
    has_vin BOOLEAN,
    image_urls TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes

The table has 7 indexes for better query performance:

1. **Primary Key**: `listing_id` (BTREE)
2. **Price**: `idx_turbo_az_price` on `price_azn` (BTREE)
3. **Make**: `idx_turbo_az_make` on `make` (BTREE)
4. **City**: `idx_turbo_az_city` on `city` (BTREE)
5. **Year**: `idx_turbo_az_year` on `year` (BTREE)
6. **Scraped**: `idx_turbo_az_scraped_at` on `scraped_at` (BTREE)
7. **Phone**: `idx_turbo_az_seller_phone_gin` on `seller_phone` (GIN)

The GIN index on `seller_phone` enables fast JSONB queries like:
```sql
-- Find listings with specific phone
WHERE seller_phone @> '["994501234567"]'::jsonb

-- Count phone numbers
WHERE jsonb_array_length(seller_phone) > 1
```

## Workflow

1. **Scraper starts**: Reads configuration from `.env`
2. **Scrapes pages**: Collects listing data in memory
3. **Auto-save interval**: Saves progress every 50 listings (optional)
4. **Scraping complete**: Calls `save_to_postgres()`
5. **Data processing**: Converts phones to JSONB, prepares batch
6. **Database insert**: Executes batch upsert in PostgreSQL
7. **Logging**: Reports success/failure and count

## Error Handling

The auto-save feature has robust error handling:

```python
# Missing DATABASE_URL
if not DATABASE_URL:
    logger.error("DATABASE_URL not found in environment variables")
    logger.error("Skipping PostgreSQL save")
    return

# Database connection errors
try:
    conn = psycopg2.connect(DATABASE_URL)
except psycopg2.Error as e:
    logger.error(f"Failed to connect to PostgreSQL: {e}")
    return

# Insert errors
try:
    execute_batch(cursor, insert_sql, data_to_insert, page_size=100)
    conn.commit()
except Exception as e:
    logger.error(f"Failed to save to PostgreSQL: {e}")
    conn.rollback()
```

## Environment Variables

Required in `.env` file:

```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

In GitHub Actions, set as repository secret:
```bash
gh secret set DATABASE_URL
```

## Benefits

1. **No file management**: No need to handle CSV files
2. **Real-time updates**: Data available in database immediately
3. **No duplicates**: Upsert logic prevents duplicate entries
4. **Better querying**: SQL queries instead of CSV parsing
5. **JSONB flexibility**: Easy to work with multiple phone numbers
6. **Scalability**: Database handles large datasets efficiently
7. **GitHub Actions friendly**: Works seamlessly in automated workflows

## Testing

Test the auto-save feature with 1 page:

```bash
# Update .env
echo "END_PAGE=1" >> .env

# Run scraper
cd scripts
python turbo_scraper.py

# Check results in PostgreSQL
psql $DATABASE_URL -c "SELECT COUNT(*) FROM scraping.turbo_az;"
```

## Performance

From actual test (1 page = 36 listings):
- Scraping time: ~230 seconds
- Database save: < 1 second
- Total listings: 36
- Batch size: 100
- Cost: $0.009

Estimated for full scrape (1770 pages):
- Total listings: ~60,000-70,000
- Database save: ~10-15 seconds
- Cost: ~$15.75

## Monitoring

Check scraper logs for save status:

```bash
# During scraping
tail -f scripts/scraper.log

# Look for these messages:
# ✓ Saved 36 listings to PostgreSQL
# Database save completed: 36 total records
```

In GitHub Actions:
```bash
# View workflow runs
gh run list --workflow=scraper.yml

# View logs
gh run view <run-id> --log
```

## Troubleshooting

### Issue: "DATABASE_URL not found"
**Solution**: Check `.env` file has `DATABASE_URL` set

### Issue: "Failed to connect to PostgreSQL"
**Solution**: Verify database URL is correct and database is accessible

### Issue: "Insert failed"
**Solution**: Check database schema matches expected structure

### Issue: "No listings to save"
**Solution**: Scraper found no data, check scraping logic

## Comparison: Before vs After

### Before (CSV-based):
```python
# Save to CSV file
save_to_csv()

# Manual import needed
import_to_postgres.py
```

### After (Auto-save):
```python
# Automatic database save
save_to_postgres()

# No manual steps needed
```

## Future Enhancements

Potential improvements:
- Incremental saves during scraping (not just at the end)
- Separate table for phone numbers with relationships
- Database-level deduplication checks
- Historical tracking of price changes
- Seller database with contact aggregation
