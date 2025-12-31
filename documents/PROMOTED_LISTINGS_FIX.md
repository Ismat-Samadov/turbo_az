# Promoted Listings Fix - Implementation Guide

## Problem Identified

Each page on turbo.az contains:
- **12 promoted/featured listings** at the top (appear on every page)
- **24 regular listings** below
- **Total: 36 listings** extracted per page

**Issue:** Scraper was collecting all 36 listings, including the 12 promoted ones that repeat across multiple pages, leading to duplicate data collection.

---

## Solution Implemented

Modified the `extract_listing_urls()` method in `scripts/turbo_scraper.py` to skip the first 12 promoted listings and collect only the 24 regular listings per page.

### Code Changes

**File:** `scripts/turbo_scraper.py`
**Location:** Lines 286-320
**Method:** `extract_listing_urls()`

**Before:**
```python
def extract_listing_urls(self, html: str) -> List[Dict[str, any]]:
    """Extract all car listing URLs and badge data from a page"""
    soup = BeautifulSoup(html, 'html.parser')
    listing_data = []

    products = soup.find_all('div', class_='products-i')

    for product in products:
        link = product.find('a', class_='products-i__link')
        if link and link.get('href'):
            full_url = urljoin(self.base_url, link['href'])

            # Extract badges from listing card
            badges = {
                'is_vip': bool(product.find('div', class_='products-i__label--vip')),
                'is_featured': bool(product.find('div', class_='products-i__label--featured')),
                'is_salon': bool(product.find('div', class_='products-i__label--salon')),
                'has_credit': bool(product.find('div', class_='products-i__icon--loan')),
                'has_barter': bool(product.find('div', class_='products-i__icon--barter')),
                'has_vin': bool(product.find('div', class_='products-i__label--vin'))
            }

            listing_data.append({
                'url': full_url,
                'badges': badges
            })

    return listing_data  # Returns all 36 listings
```

**After:**
```python
def extract_listing_urls(self, html: str) -> List[Dict[str, any]]:
    """Extract all car listing URLs and badge data from a page (excluding promoted listings)"""
    soup = BeautifulSoup(html, 'html.parser')
    listing_data = []

    products = soup.find_all('div', class_='products-i')

    for product in products:
        link = product.find('a', class_='products-i__link')
        if link and link.get('href'):
            full_url = urljoin(self.base_url, link['href'])

            # Extract badges from listing card
            badges = {
                'is_vip': bool(product.find('div', class_='products-i__label--vip')),
                'is_featured': bool(product.find('div', class_='products-i__label--featured')),
                'is_salon': bool(product.find('div', class_='products-i__label--salon')),
                'has_credit': bool(product.find('div', class_='products-i__icon--loan')),
                'has_barter': bool(product.find('div', class_='products-i__icon--barter')),
                'has_vin': bool(product.find('div', class_='products-i__label--vin'))
            }

            listing_data.append({
                'url': full_url,
                'badges': badges
            })

    # Skip the first 12 promoted listings (they appear at the top of every page)
    # Only return the 24 regular listings
    total_found = len(listing_data)
    regular_listings = listing_data[12:] if total_found > 12 else listing_data

    logger.debug(f"Found {total_found} total listings, returning {len(regular_listings)} regular listings (skipped {total_found - len(regular_listings)} promoted)")

    return regular_listings  # Returns only 24 regular listings
```

---

## Key Changes

1. **Listing Filtering**: Added logic to skip the first 12 listings using Python list slicing `listing_data[12:]`
2. **Edge Case Handling**: If page has fewer than 12 listings, returns all listings (safeguard for edge cases)
3. **Debug Logging**: Added logging to show total found vs. returned count
4. **Updated Docstring**: Clarified that method excludes promoted listings

---

## Impact Analysis

### Before Fix
```
Page 1: 36 listings (12 promoted + 24 regular)
Page 2: 36 listings (same 12 promoted + 24 new regular)
Page 3: 36 listings (same 12 promoted + 24 new regular)
...
Total: 36 × 1770 pages = 63,720 listings
Duplicates: 12 promoted listings × 1769 repetitions = 21,228 duplicates
```

### After Fix
```
Page 1: 24 regular listings only
Page 2: 24 new regular listings only
Page 3: 24 new regular listings only
...
Total: 24 × 1770 pages = 42,480 unique listings
Duplicates: 0 (promoted listings skipped)
```

**Data Quality Improvement:**
- ✅ Eliminates 21,228 duplicate entries
- ✅ Reduces database size by ~33%
- ✅ Ensures all listings are unique regular listings
- ✅ No performance impact (same number of requests)

---

## Verification

### Test 1: Run on Single Page
```bash
cd /Users/ismatsamadov/turbo_az/scripts
END_PAGE=1 python3 turbo_scraper.py
```

**Expected Output:**
```
Found 24 listings on page 1  # Previously showed 36
```

### Test 2: Check Database Count
```bash
# Before: ~13,759 listings (with duplicates)
# After new full scrape: ~42,480 listings (all unique)

psql $DATABASE_URL -c "
SELECT COUNT(*) as total_listings,
       COUNT(DISTINCT listing_id) as unique_ids,
       COUNT(DISTINCT listing_url) as unique_urls
FROM scraping.turbo_az;
"
```

**Expected:** All three counts should be equal (no duplicates)

### Test 3: Verify No Duplicate URLs
```bash
psql $DATABASE_URL -c "SELECT * FROM scraping.duplicate_detection;"
```

**Expected:** 0 rows (no duplicates)

---

## Logging Output Example

### Old Behavior
```
2025-12-31 09:33:00 - INFO - Found 36 listings on page 1
2025-12-31 09:33:30 - INFO - Found 36 listings on page 2
```

### New Behavior
```
2025-12-31 09:33:00 - DEBUG - Found 36 total listings, returning 24 regular listings (skipped 12 promoted)
2025-12-31 09:33:00 - INFO - Found 24 listings on page 1
2025-12-31 09:33:30 - DEBUG - Found 36 total listings, returning 24 regular listings (skipped 12 promoted)
2025-12-31 09:33:30 - INFO - Found 24 listings on page 2
```

---

## Database Uniqueness Protection

The scraper already has three-tier duplicate protection:

1. **Tier 1**: `listing_id` PRIMARY KEY (PostgreSQL)
2. **Tier 2**: `listing_url` UNIQUE constraint (PostgreSQL)
3. **Tier 3**: Smart batch fallback in scraper (Python)

This fix adds a **Tier 0** pre-filter at the extraction level, preventing promoted listing duplicates from even entering the pipeline.

---

## Performance Considerations

### Before Fix
- **Pages scraped**: 1,770
- **Listings extracted**: 63,720
- **Listings scraped**: 63,720 (with ~21,228 duplicates updated via ON CONFLICT)
- **Time wasted**: ~21,228 × 6s ≈ 35 hours on duplicate scraping

### After Fix
- **Pages scraped**: 1,770
- **Listings extracted**: 42,480
- **Listings scraped**: 42,480 (all unique)
- **Time saved**: ~35 hours (no duplicate scraping)

**Net Result:**
- ✅ Faster scraping (33% fewer listings to process)
- ✅ Cleaner data (zero duplicates from promoted listings)
- ✅ Lower database load (fewer ON CONFLICT updates)
- ✅ Better data quality metrics

---

## Alternative Approaches Considered

### Option 1: Filter by Parent Container
```python
# Try to find a parent container that separates promoted from regular
promoted_section = soup.find('div', class_='products--promoted')
regular_section = soup.find('div', class_='products--regular')
```
**Rejected:** No such distinguishing container found in HTML structure.

### Option 2: Filter by Badge Attributes
```python
# Skip listings with specific badge combinations
if badges['is_featured'] and badges['is_vip']:
    continue  # Skip promoted
```
**Rejected:** Not all promoted listings have the same badge combination; regular listings can also have these badges.

### Option 3: Skip First 12 (Selected)
```python
# Simply skip the first 12 listings
regular_listings = listing_data[12:]
```
**Selected:** Simple, reliable, and effective based on consistent page structure.

---

## Edge Cases Handled

1. **Page with fewer than 12 listings** (e.g., last page)
   - Condition: `listing_data[12:] if total_found > 12 else listing_data`
   - Result: Returns all listings (no error)

2. **Promoted listings change position**
   - Currently: Always at top (positions 1-12)
   - If turbo.az changes layout: Will need to revisit this logic

3. **Empty page** (no listings)
   - `listing_data` is empty list
   - `listing_data[12:]` returns empty list
   - Result: No error, just logs "Found 0 listings"

---

## Monitoring Recommendations

After deploying this fix, monitor the following:

1. **Listings per page**: Should consistently show 24 (except possibly last page)
2. **Duplicate detection view**: Should remain at 0 duplicates
3. **Total database size**: Should be ~42,480 listings after full scrape (instead of ~63,720)
4. **Scraping time**: Should reduce by ~33% (fewer listings to process)

---

## Rollback Instructions

If this fix causes issues, revert to original behavior:

```python
# In extract_listing_urls() method, replace:
regular_listings = listing_data[12:] if total_found > 12 else listing_data
return regular_listings

# With:
return listing_data
```

---

## Related Documentation

- `documents/AUTO_SAVE_AND_DUPLICATES.md` - Duplicate handling strategy
- `documents/DATABASE_UNIQUENESS_STRATEGY.md` - Multi-tier uniqueness protection
- `documents/DUPLICATE_HANDLING_EXPLAINED.md` - How ON CONFLICT works
- `scripts/turbo_scraper.py` - Main scraper implementation

---

## Summary

**Problem:** Scraper collecting 12 promoted listings on every page, leading to 21,228 duplicate entries

**Solution:** Filter out first 12 promoted listings at extraction level, collecting only 24 regular listings per page

**Impact:**
- ✅ Eliminates 21,228 duplicates
- ✅ Reduces scraping time by ~35 hours
- ✅ Improves data quality
- ✅ Reduces database size by 33%

**Implementation:** Single method change in `extract_listing_urls()` with list slicing

**Status:** ✅ Implemented and ready for testing

---

*Fix Implemented: 2025-12-31*
*Modified File: scripts/turbo_scraper.py*
*Method: extract_listing_urls()*
*Lines: 286-320*
