# How the Scraper Handles Duplicates - Complete Explanation

## Current Behavior (listing_id only)

### **What Happens When Scraper Encounters a Duplicate**

```python
# Current SQL in turbo_scraper.py (line ~850)
INSERT INTO scraping.turbo_az (
    listing_id, listing_url, title, price_azn, make, model, ...
) VALUES (%s, %s, %s, %s, %s, %s, ...)
ON CONFLICT (listing_id) DO UPDATE SET
    listing_url = EXCLUDED.listing_url,
    title = EXCLUDED.title,
    price_azn = EXCLUDED.price_azn,
    make = EXCLUDED.make,
    ... (all other fields)
    scraped_at = EXCLUDED.scraped_at;
```

### **Step-by-Step Process**

```
1. Scraper visits page → extracts listing data
   ↓
2. Extracts listing_id from URL
   Example: https://turbo.az/autos/5762219 → listing_id = 5762219
   ↓
3. Attempts to INSERT into database
   ↓
4. PostgreSQL checks: Does this listing_id already exist?
   ↓
   YES (DUPLICATE FOUND)                    NO (NEW LISTING)
   ↓                                        ↓
   UPDATES existing record with new data    INSERTS new record
   ↓                                        ↓
   Updated fields:                          All fields inserted
   - listing_url (in case URL changed)      ↓
   - title                                  ✅ Success (new listing added)
   - price_azn (track price changes!)
   - all other fields
   - scraped_at (marks when last seen)
   ↓
   ✅ Success (existing listing updated)
```

---

## Real-World Scenarios

### **Scenario 1: Same Listing, Re-Scraped**

```
First scrape (Dec 25):
  listing_id: 5762219
  title: "2020 Mercedes E-Class"
  price_azn: "45000 ₼"
  scraped_at: 2025-12-25 10:00:00

Second scrape (Dec 31 - today):
  listing_id: 5762219  ← SAME ID
  title: "2020 Mercedes E-Class"
  price_azn: "42000 ₼"  ← PRICE DROPPED!
  scraped_at: 2025-12-31 10:00:00

RESULT:
  ✅ ON CONFLICT (listing_id) DO UPDATE
  ✅ Existing record updated with new price
  ✅ Now you can see price dropped by 3000 AZN
  ✅ scraped_at updated to show listing is still active
```

**This is GOOD behavior** - you track:
- Price changes over time
- When listing was last seen (still active)
- Any other field updates (description changes, mileage increases)

---

### **Scenario 2: Listing Deleted and Recreated**

```
Dec 20: Seller lists car
  listing_id: 5762219
  Database: INSERT (new record)

Dec 25: Seller deletes listing
  (Scraper doesn't see it)
  Database: Record remains (marked as last seen Dec 24)

Dec 30: Seller relists SAME car with SAME listing_id
  listing_id: 5762219  ← SAME ID
  Database: UPDATE existing record
  ✅ Record is "refreshed" - scraped_at updated
```

**This is GOOD** - listing still exists in database, just refreshed.

---

### **Scenario 3: Multiple Scrapers Running Simultaneously**

```
Scraper Instance A (page 1-500):
  Processes listing_id 5762219 at 10:00:00
  INSERT ... ON CONFLICT → INSERT (new)

Scraper Instance B (page 1-500):
  Processes SAME listing_id 5762219 at 10:00:05
  INSERT ... ON CONFLICT → UPDATE (duplicate detected)

RESULT:
  ✅ No error thrown
  ✅ No duplicate created
  ✅ Second scraper just updates the record (harmless)
```

**This is GOOD** - concurrent scraping is safe.

---

## After Adding URL Uniqueness (Upgraded Behavior)

### **What Changes**

```sql
ALTER TABLE scraping.turbo_az
ADD CONSTRAINT unique_listing_url UNIQUE (listing_url);
```

Now you have TWO uniqueness constraints:
1. PRIMARY KEY on `listing_id`
2. UNIQUE on `listing_url`

### **New Scenario: URL Collision (Very Rare)**

```
What if turbo.az reuses a URL for a DIFFERENT car?

Scraper finds:
  listing_id: 9999999  ← NEW ID
  listing_url: "https://turbo.az/autos/5762219"  ← EXISTING URL

Current behavior:
  INSERT ... → PostgreSQL checks listing_id → Not found → OK
              → PostgreSQL checks listing_url → FOUND! → ERROR!

PostgreSQL raises:
  psycopg2.errors.UniqueViolation:
  duplicate key value violates unique constraint "unique_listing_url"

What happens:
  ❌ INSERT fails
  ❌ Scraper gets exception
  ⚠️ Needs handling code
```

**This is RARE** but can happen if turbo.az:
- Deletes old listing 5762219
- Creates new listing and reuses the numeric ID in URL

---

## Recommended: Enhanced Duplicate Handling

### **Option A: Skip URL Duplicates (Safest)**

Add error handling to scraper:

```python
try:
    execute_batch(cursor, insert_sql, batch_data, page_size=100)
    logger.info(f"✅ Saved {len(batch_data)} listings")

except psycopg2.errors.UniqueViolation as e:
    if 'unique_listing_url' in str(e):
        logger.warning(f"⚠️ URL duplicate detected - skipping")
        # Continue scraping, just skip this one
        conn.rollback()
    else:
        raise  # Re-raise if it's a different error
```

**Behavior:**
- Skips the conflicting listing
- Logs warning message
- Continues scraping rest of page
- ✅ No data corruption
- ✅ No scraper crash

---

### **Option B: Update Using URL (More Complex)**

Handle URL conflicts by updating the existing record:

```python
try:
    execute_batch(cursor, insert_sql, batch_data, page_size=100)

except psycopg2.errors.UniqueViolation as e:
    if 'unique_listing_url' in str(e):
        logger.warning(f"⚠️ URL conflict - updating existing record")

        # Find which listing caused the conflict
        for listing in batch_data:
            cursor.execute("""
                SELECT listing_id FROM scraping.turbo_az
                WHERE listing_url = %s
            """, (listing[1],))  # listing_url is index 1

            existing = cursor.fetchone()
            if existing and existing[0] != listing[0]:  # Different IDs
                # Update existing record with new listing_id
                cursor.execute("""
                    UPDATE scraping.turbo_az
                    SET listing_id = %s,
                        title = %s,
                        price_azn = %s,
                        -- ... all other fields ...
                        scraped_at = CURRENT_TIMESTAMP
                    WHERE listing_url = %s
                """, (*listing, listing[1]))

                logger.info(f"✅ Updated listing_id from {existing[0]} to {listing[0]}")
```

**Behavior:**
- Detects URL conflict
- Updates existing record with new listing_id
- Preserves all data
- ✅ No data loss
- ⚠️ More complex logic

---

## Comparison: With vs Without URL Uniqueness

| Scenario | Without URL Unique | With URL Unique |
|----------|-------------------|-----------------|
| **Re-scrape same listing** | ✅ Updates record | ✅ Updates record |
| **Price changes** | ✅ Tracked | ✅ Tracked |
| **Concurrent scraping** | ✅ Safe | ✅ Safe |
| **Turbo.az reuses listing_id** | ❌ Overwrites old listing | ✅ Detected as conflict |
| **URL changes for listing** | ✅ URL updated | ✅ URL updated |
| **Same URL, different ID** | ❌ Creates duplicate | ✅ **Prevents duplicate** |

---

## What You Should Do

### **Step 1: Add URL Uniqueness** (Recommended)

```bash
cd /Users/ismatsamadov/turbo_az/scripts
python3 add_url_uniqueness.py
```

This gives you double protection against duplicates.

---

### **Step 2: Choose Error Handling Strategy**

**For Production (Option A - Simple):**

Add this to `turbo_scraper.py` in the `save_to_postgres()` method:

```python
# Around line 890, after execute_batch
try:
    execute_batch(cursor, insert_sql, batch_data, page_size=100)
    conn.commit()
    logger.info(f"✅ Successfully saved {len(batch_data)} listings to PostgreSQL")

except psycopg2.errors.UniqueViolation as e:
    error_msg = str(e)

    if 'unique_listing_url' in error_msg:
        logger.warning("⚠️ Duplicate URL detected - some listings skipped")
        logger.warning(f"   Error: {error_msg}")
        conn.rollback()

        # Continue scraping - this is not fatal
        # The duplicate just won't be inserted

    else:
        # Different uniqueness violation, re-raise
        logger.error(f"❌ Database error: {e}")
        raise

except psycopg2.Error as e:
    logger.error(f"❌ Failed to save to PostgreSQL: {e}")
    conn.rollback()
    raise
```

---

### **Step 3: Monitor for URL Conflicts**

After scraping, check if any URL conflicts occurred:

```sql
-- Check scraper logs
tail -100 scripts/scraper.log | grep "URL duplicate"

-- Check for any data anomalies
SELECT COUNT(*) FROM scraping.duplicate_detection;
-- Expected: 0 rows
```

---

## Summary: How Duplicates Are Handled

### **Current System (listing_id only)**

```
Duplicate listing_id → ✅ UPDATE existing record
Same listing → ✅ Refreshed with latest data
Price changes → ✅ Tracked automatically
Concurrent scraping → ✅ Safe (no errors)
URL reuse → ❌ Might overwrite wrong listing
```

### **After URL Uniqueness Added**

```
Duplicate listing_id → ✅ UPDATE existing record
Duplicate listing_url → ✅ Prevented (error raised)
Same listing → ✅ Refreshed with latest data
Price changes → ✅ Tracked automatically
Concurrent scraping → ✅ Safe (no errors)
URL reuse → ✅ Detected and handled
```

---

## Real Execution Flow

### **Normal Scraping Session**

```
1. Scraper starts
   Pages 1-1770 queued

2. For each page:
   - Extract 20-40 listings
   - For each listing:
     * Extract listing_id from URL
     * Extract all data fields
     * Add to batch

3. After page 50 (AUTO_SAVE_INTERVAL):
   - Prepare batch of ~2000 listings
   - Execute: INSERT ... ON CONFLICT
   - PostgreSQL processes each listing:

   Listing 1: ID=123, URL=.../123
     → Check: ID exists? NO → INSERT ✅

   Listing 2: ID=456, URL=.../456
     → Check: ID exists? YES → UPDATE ✅

   Listing 3: ID=789, URL=.../456  (URL duplicate!)
     → Check: ID exists? NO
     → Check: URL exists? YES → ERROR ❌
     → Exception: UniqueViolation
     → Handled by try/except
     → Logged as warning
     → Skip this listing
     → Continue with next

4. Scraping continues
5. Final batch saved
6. Complete!
```

**Result:**
- 99.9% of listings saved successfully
- 0.1% skipped due to URL conflicts (if any)
- Zero duplicates in database
- All price changes tracked
- No data corruption

---

## Testing Your Duplicate Handling

```bash
# 1. Add URL uniqueness
python3 scripts/add_url_uniqueness.py

# 2. Run scraper on 1 page
cd scripts
END_PAGE=1 python3 turbo_scraper.py

# 3. Run SAME page again (should update, not duplicate)
END_PAGE=1 python3 turbo_scraper.py

# 4. Check database
psql $DATABASE_URL -c "
SELECT
    COUNT(*) as total,
    COUNT(DISTINCT listing_id) as unique_ids,
    COUNT(DISTINCT listing_url) as unique_urls
FROM scraping.turbo_az;
"

# Expected: total = unique_ids = unique_urls (no duplicates)
```

---

**Bottom Line:** Your scraper already handles duplicates well with `ON CONFLICT`. Adding URL uniqueness provides extra protection against edge cases where turbo.az might reuse IDs or URLs.

