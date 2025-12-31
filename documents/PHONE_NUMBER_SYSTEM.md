# Phone Number System - Complete Guide

## Current Status: ✅ Working Perfectly!

Phone numbers are **already stored correctly** as JSONB arrays in PostgreSQL.

## Database Schema

```sql
CREATE TABLE scraping.turbo_az (
    ...
    seller_phone JSONB,  -- Array of phone numbers
    ...
);
```

### Example Data

```json
-- Single phone
["+ 994 55 123 45 67"]

-- Multiple phones
["+994 50 400 19 24", "+994 50 444 19 24", "+994 12 525 51 51"]

-- Short codes
["*5544", "+994 51 638 89 00"]
```

## Statistics (as of 2025-12-31)

- **Total listings**: 13,828
- **Listings with phones**: 1,324 (9.6%)

### Distribution by Phone Count

| Phone Count | Listings | Percentage |
|-------------|----------|------------|
| 1 phone | 998 | 75.4% |
| 2 phones | 133 | 10.0% |
| 3 phones | 107 | 8.1% |
| 4+ phones | 86 | 6.5% |

### Maximum Phones

Some listings have up to **5 phone numbers** (dealers/salons).

---

## SQL Query Examples

### 1. Get All Listings with Phones

```sql
SELECT listing_id, title, seller_phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 2. Get Listings with Exactly N Phones

```sql
-- Get listings with exactly 3 phones
SELECT listing_id, title, seller_phone
FROM scraping.turbo_az
WHERE jsonb_array_length(seller_phone) = 3;
```

### 3. Extract First Phone Number

```sql
-- Get first phone (index 0)
SELECT
    listing_id,
    title,
    seller_phone->0 as first_phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 4. Extract Second Phone Number

```sql
-- Get second phone (index 1)
SELECT
    listing_id,
    title,
    seller_phone->0 as first_phone,
    seller_phone->1 as second_phone
FROM scraping.turbo_az
WHERE jsonb_array_length(seller_phone) >= 2;
```

### 5. Extract All Phones as Separate Rows

```sql
-- Explode phone array into separate rows
SELECT
    listing_id,
    title,
    jsonb_array_elements_text(seller_phone) as phone
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
```

### 6. Search by Phone Number

```sql
-- Find all listings with a specific phone
SELECT listing_id, title, seller_phone
FROM scraping.turbo_az
WHERE seller_phone ? '+994 50 400 19 24';
```

### 7. Find Dealers (Multiple Listings with Same Phone)

```sql
-- Find phones used in multiple listings (dealers)
SELECT
    phone,
    COUNT(*) as listing_count,
    array_agg(listing_id) as listing_ids
FROM scraping.turbo_az,
     jsonb_array_elements_text(seller_phone) as phone
GROUP BY phone
HAVING COUNT(*) > 1
ORDER BY listing_count DESC;
```

### 8. Get Phone Count Distribution

```sql
-- Statistics on phone count per listing
SELECT
    jsonb_array_length(seller_phone) as phone_count,
    COUNT(*) as listings
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL
GROUP BY jsonb_array_length(seller_phone)
ORDER BY phone_count;
```

---

## Python Examples

### Using psycopg2 (Direct)

```python
import psycopg2
import json

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Get listing with phones
cursor.execute("""
    SELECT listing_id, seller_phone
    FROM scraping.turbo_az
    WHERE listing_id = 7265016
""")

listing_id, phones = cursor.fetchone()

# phones is already a Python list!
print(f"Listing {listing_id} has {len(phones)} phones:")
for i, phone in enumerate(phones, 1):
    print(f"  Phone {i}: {phone}")

# Output:
# Listing 7265016 has 2 phones:
#   Phone 1: +994 12 404 83 95
#   Phone 2: +994 55 444 47 00
```

### Using Phone Utils

```python
from scripts.phone_utils import PhoneUtils

utils = PhoneUtils()

# Get all listings with 3 phones
listings = utils.get_listings_with_phones(phone_count=3)

for listing in listings:
    print(f"{listing['title']}:")
    for phone in listing['phones']:
        print(f"  - {phone}")

utils.close()
```

---

## How the Scraper Works

### Current Implementation (✅ Correct)

In `turbo_scraper.py`:

```python
def parse_phone_numbers(phone_str):
    """Convert phone string to JSON array"""
    if not phone_str or phone_str == '':
        return None

    # Split by pipe separator
    phones = [p.strip() for p in str(phone_str).split('|') if p.strip()]

    # Return as JSON array
    return json.dumps(phones) if phones else None

# When saving to database:
seller_phone = parse_phone_numbers(phone_numbers)

# SQL insert:
INSERT INTO scraping.turbo_az (seller_phone, ...)
VALUES (%s, ...)  -- psycopg2 automatically handles JSON
```

### How Phone Extraction Works

1. **Scraper visits listing page**
2. **Calls AJAX endpoint** to get phones: `/autos/{listing_id}/show_phones`
3. **AJAX returns JSON**:
   ```json
   {
     "phones": [
       {"primary": "+994 50 400 19 24", "raw": "0504001924"},
       {"primary": "+994 50 444 19 24", "raw": "0504441924"},
       {"primary": "+994 12 525 51 51", "raw": "0125255151"}
     ]
   }
   ```
4. **Scraper extracts** `primary` field from each phone
5. **Joins with pipe**: `+994 50 400 19 24 | +994 50 444 19 24 | +994 12 525 51 51`
6. **Saves to database** as JSONB array: `["+994 50 400 19 24", "+994 50 444 19 24", "+994 12 525 51 51"]`

---

## Dashboard Integration

### Prisma Schema (Already Correct)

```prisma
model TurboListing {
  ...
  sellerPhone   Json?     @map("seller_phone")
  ...
}
```

### TypeScript Usage

```typescript
// Fetch listing
const listing = await prisma.turboListing.findUnique({
  where: { listingId: 7265016 }
})

// phones is automatically parsed as array
const phones = listing.sellerPhone as string[]

console.log(`Phones: ${phones.join(', ')}`)
// Output: Phones: +994 12 404 83 95, +994 55 444 47 00
```

### React Component Example

```tsx
function ListingCard({ listing }) {
  const phones = listing.sellerPhone as string[]

  return (
    <div>
      <h3>{listing.title}</h3>
      <div>
        {phones && phones.length > 0 && (
          <div>
            <strong>Contact:</strong>
            {phones.map((phone, i) => (
              <a key={i} href={`tel:${phone}`}>
                {phone}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## Useful Queries for Business Analysis

### 1. Top Dealers by Listing Count

```sql
-- Find dealers with most listings (by phone number)
SELECT
    phone,
    COUNT(DISTINCT listing_id) as total_listings,
    array_agg(DISTINCT make) as brands_sold,
    AVG(CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS NUMERIC)) as avg_price
FROM scraping.turbo_az,
     jsonb_array_elements_text(seller_phone) as phone
WHERE seller_phone IS NOT NULL
GROUP BY phone
HAVING COUNT(*) >= 5
ORDER BY total_listings DESC
LIMIT 20;
```

### 2. Listings Without Phones (Sales Opportunity)

```sql
-- Find high-value listings without contact info
SELECT
    listing_id,
    title,
    price_azn,
    city,
    year
FROM scraping.turbo_az
WHERE seller_phone IS NULL
  AND price_azn IS NOT NULL
ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS NUMERIC) DESC
LIMIT 100;
```

### 3. Phone Format Analysis

```sql
-- Analyze phone number formats
SELECT
    CASE
        WHEN phone LIKE '+994%' THEN 'International (+994)'
        WHEN phone LIKE '*%' THEN 'Short code (*XXXX)'
        WHEN phone ~ '^[0-9]{3,4}$' THEN 'Short number'
        ELSE 'Other format'
    END as phone_format,
    COUNT(*) as count
FROM scraping.turbo_az,
     jsonb_array_elements_text(seller_phone) as phone
GROUP BY phone_format
ORDER BY count DESC;
```

---

## Export Phone Numbers

### To CSV

```python
from scripts.phone_utils import PhoneUtils

utils = PhoneUtils()
utils.export_phones_csv('dealer_phones.csv')
utils.close()
```

### To Excel (with pandas)

```python
import pandas as pd
import psycopg2

conn = psycopg2.connect(DATABASE_URL)

# Query with phone explosion
df = pd.read_sql("""
    SELECT
        listing_id,
        title,
        make,
        model,
        price_azn,
        city,
        jsonb_array_elements_text(seller_phone) as phone
    FROM scraping.turbo_az
    WHERE seller_phone IS NOT NULL
""", conn)

df.to_excel('phones.xlsx', index=False)
```

---

## Best Practices

### ✅ DO

- Use `jsonb_array_length()` to count phones
- Use `->0`, `->1` for array indexing
- Use `jsonb_array_elements_text()` to explode arrays
- Use `?` operator for phone existence checks
- Keep phones as JSONB arrays (current format)

### ❌ DON'T

- Don't convert to text with pipes (`phone1 | phone2`)
- Don't create separate columns (`phone1`, `phone2`, `phone3`)
- Don't store as comma-separated strings
- Don't use VARCHAR for phone storage

---

## Performance Tips

### Create Index for Phone Searches

```sql
-- GIN index for JSONB containment searches
CREATE INDEX idx_seller_phone_gin
ON scraping.turbo_az
USING GIN (seller_phone);

-- Functional index for phone count
CREATE INDEX idx_seller_phone_count
ON scraping.turbo_az ((jsonb_array_length(seller_phone)));
```

### Optimize Common Queries

```sql
-- Faster phone existence check
SELECT COUNT(*)
FROM scraping.turbo_az
WHERE seller_phone IS NOT NULL;
-- Uses IS NOT NULL check (fast)

-- Faster dealer identification
WITH phone_usage AS (
    SELECT
        jsonb_array_elements_text(seller_phone) as phone,
        COUNT(*) as count
    FROM scraping.turbo_az
    WHERE seller_phone IS NOT NULL
    GROUP BY phone
)
SELECT * FROM phone_usage WHERE count > 1;
```

---

## Summary

### Current State: ✅ Perfect!

- ✅ Phones stored as JSONB arrays
- ✅ Supports 1 to 5+ phones per listing
- ✅ Easy to query with PostgreSQL JSONB functions
- ✅ No normalization needed
- ✅ Scraper working correctly
- ✅ Dashboard integration ready

### No Action Required

The phone number system is **production-ready and working as designed**.

---

## Tools Available

1. **analyze_phone_numbers.py** - Analyze current phone data
2. **phone_utils.py** - Helper functions for phone queries
3. **SQL examples** - Copy-paste queries above

---

**Last Updated**: 2025-12-31
**Status**: ✅ Production Ready
**Phone Format**: JSONB Array (Optimal)
