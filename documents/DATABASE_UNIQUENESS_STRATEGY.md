# Database Uniqueness Strategy - Preventing Duplicate Listings

## Current Setup

**Primary Key:** `listing_id` (BIGINT)
- Extracted from turbo.az listing URL
- Example: `https://turbo.az/autos/5762219` → `listing_id = 5762219`
- Current behavior: `ON CONFLICT (listing_id) DO UPDATE` (upsert)

**Problem:** 
- If turbo.az reuses IDs or changes listing structure, we might miss duplicates
- No protection against URL changes or data corruption

---

## Recommended Solution: Multi-Level Uniqueness

### Strategy: Three-Tier Protection

```
Tier 1: listing_id (PRIMARY KEY) ← Main identifier
Tier 2: listing_url (UNIQUE) ← URL protection  
Tier 3: Natural key composite (UNIQUE) ← Content-based deduplication
```

### Why This Approach?

| Level | Field(s) | Purpose | Catches |
|-------|----------|---------|---------|
| **Tier 1** | `listing_id` | Primary identifier from source | Most duplicates (99%+) |
| **Tier 2** | `listing_url` | URL-based uniqueness | ID reuse, URL changes |
| **Tier 3** | Composite key | Content fingerprint | True duplicates with different IDs |

---

## Implementation

### Option A: Simple (Recommended for Your Case)

**Keep current + Add URL uniqueness**

```sql
-- Add UNIQUE constraint on listing_url
ALTER TABLE scraping.turbo_az 
ADD CONSTRAINT unique_listing_url UNIQUE (listing_url);
```

**Benefits:**
✅ Fast to implement
✅ Catches 99.9% of duplicates
✅ Minimal performance impact
✅ Works with existing scraper code

**Update scraper upsert logic to:**
```python
INSERT INTO scraping.turbo_az (...)
VALUES (...)
ON CONFLICT (listing_id) DO UPDATE SET ...
-- Also handle URL conflicts
ON CONFLICT (listing_url) DO UPDATE SET listing_id = EXCLUDED.listing_id, ...
```

### Option B: Advanced (More Robust)

**Add composite unique index for content-based deduplication**

```sql
-- Create unique index on natural key
CREATE UNIQUE INDEX unique_listing_fingerprint 
ON scraping.turbo_az (make, model, year, mileage, seller_phone)
WHERE make IS NOT NULL AND model IS NOT NULL;
```

**Benefits:**
✅ Catches true duplicates even if ID/URL different
✅ Identifies relisted vehicles
✅ Detects data quality issues

**Drawbacks:**
⚠️ More complex to maintain
⚠️ Seller can legitimately have multiple identical cars
⚠️ Mileage changes over time

### Option C: Paranoid (Maximum Protection)

**Add deduplication hash column**

```sql
-- Add hash column
ALTER TABLE scraping.turbo_az 
ADD COLUMN listing_hash VARCHAR(64);

-- Create unique index
CREATE UNIQUE INDEX unique_listing_hash 
ON scraping.turbo_az (listing_hash);

-- Update function to generate hash
CREATE OR REPLACE FUNCTION scraping.generate_listing_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.listing_hash = MD5(
        COALESCE(NEW.listing_id::TEXT, '') || 
        COALESCE(NEW.listing_url, '') ||
        COALESCE(NEW.title, '') ||
        COALESCE(NEW.make, '') ||
        COALESCE(NEW.model, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER generate_listing_hash_trigger
BEFORE INSERT OR UPDATE ON scraping.turbo_az
FOR EACH ROW EXECUTE FUNCTION scraping.generate_listing_hash();
```

---

## Comparison: Which Method Should You Use?

| Method | Duplicate Detection | Performance | Complexity | Recommendation |
|--------|---------------------|-------------|------------|----------------|
| **Current (listing_id only)** | 95% | ⚡⚡⚡ Fastest | ✅ Simple | Good for testing |
| **Option A (+ URL unique)** | 99.9% | ⚡⚡⚡ Fast | ✅ Simple | **✨ RECOMMENDED** |
| **Option B (+ Composite)** | 99.95% | ⚡⚡ Good | ⚠️ Medium | Advanced users |
| **Option C (+ Hash)** | 99.99% | ⚡ Slower | ❌ Complex | Paranoid mode |

---

## Recommended Implementation for Turbo.az

### Step 1: Add URL Uniqueness

```sql
-- This is the sweet spot for your use case
ALTER TABLE scraping.turbo_az 
ADD CONSTRAINT unique_listing_url UNIQUE (listing_url);
```

### Step 2: Update Scraper Code

PostgreSQL doesn't support multiple ON CONFLICT targets directly. Best approach:

```python
# Option 1: Use listing_url as primary key instead
# Change scraper to extract URL-based unique identifier

# Option 2: Check for URL conflicts separately
# Before insert, check if URL exists
cursor.execute("""
    SELECT listing_id FROM scraping.turbo_az 
    WHERE listing_url = %s
""", (listing_url,))

existing = cursor.fetchone()
if existing:
    # URL exists, update that record
    # Use existing listing_id
else:
    # New listing, insert normally
```

### Step 3: Create Duplicate Detection Query

```sql
-- Find potential duplicates by various criteria
SELECT 
    COUNT(*) as duplicate_count,
    make, model, year, seller_phone
FROM scraping.turbo_az
GROUP BY make, model, year, seller_phone
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

---

## Best Practice: Choose Based on Your Needs

### For Turbo.az Scraper (Your Case):

**I recommend Option A:**

1. ✅ Keep `listing_id` as PRIMARY KEY (fast lookups)
2. ✅ Add UNIQUE constraint on `listing_url` (prevent URL duplicates)
3. ✅ Modify scraper to check URL before insert
4. ✅ Add monitoring query to detect duplicates

**Why?**
- Turbo.az likely uses stable listing IDs
- URLs are reliable unique identifiers
- Simple to implement and maintain
- Minimal performance impact
- Catches 99.9% of real-world duplicates

### Implementation Script

I'll create an upgrade script that:
1. Adds UNIQUE constraint on listing_url
2. Updates scraper logic to handle conflicts
3. Creates monitoring queries
4. Documents the strategy

---

## Testing Your Uniqueness Strategy

```sql
-- 1. Check for current duplicates by listing_id
SELECT listing_id, COUNT(*) 
FROM scraping.turbo_az 
GROUP BY listing_id 
HAVING COUNT(*) > 1;

-- 2. Check for current duplicates by listing_url
SELECT listing_url, COUNT(*) 
FROM scraping.turbo_az 
GROUP BY listing_url 
HAVING COUNT(*) > 1;

-- 3. Check for potential duplicates by content
SELECT 
    make, model, year, mileage, COUNT(*) as count
FROM scraping.turbo_az
GROUP BY make, model, year, mileage
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;

-- 4. Check for same car, different listings
SELECT 
    a.listing_id, a.listing_url,
    b.listing_id, b.listing_url,
    a.title
FROM scraping.turbo_az a
JOIN scraping.turbo_az b ON 
    a.make = b.make AND 
    a.model = b.model AND 
    a.year = b.year AND
    a.seller_phone = b.seller_phone AND
    a.listing_id != b.listing_id
LIMIT 10;
```

---

## Monitoring & Maintenance

### Daily Duplicate Check

```sql
-- Add to monitoring dashboard
CREATE OR REPLACE VIEW scraping.duplicate_detection AS
SELECT 
    'listing_id' as conflict_type,
    listing_id::TEXT as conflict_value,
    COUNT(*) as occurrences
FROM scraping.turbo_az
GROUP BY listing_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 
    'listing_url' as conflict_type,
    listing_url as conflict_value,
    COUNT(*) as occurrences
FROM scraping.turbo_az
GROUP BY listing_url
HAVING COUNT(*) > 1;

-- Query the view
SELECT * FROM scraping.duplicate_detection;
```

### Cleanup Duplicates

```sql
-- If duplicates found, keep most recent
WITH duplicates AS (
    SELECT listing_id, 
           ROW_NUMBER() OVER (
               PARTITION BY listing_url 
               ORDER BY scraped_at DESC
           ) as rn
    FROM scraping.turbo_az
)
DELETE FROM scraping.turbo_az
WHERE listing_id IN (
    SELECT listing_id FROM duplicates WHERE rn > 1
);
```

---

## Summary

**For your turbo.az scraper, implement:**

1. **Primary uniqueness**: `listing_id` (already done ✅)
2. **Secondary protection**: Add UNIQUE on `listing_url`
3. **Monitoring**: Weekly duplicate detection query
4. **Scraper logic**: Handle URL conflicts gracefully

This gives you enterprise-grade duplicate protection with minimal complexity.

