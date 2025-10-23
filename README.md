# Turbo.az Async Scraper

High-speed async web scraper for turbo.az using aiohttp and asyncio.

## Features

- ✅ **Async/await with aiohttp** - Fast and reliable
- ✅ **Bright Data proxy support** - Residential proxies
- ✅ **Phone numbers extracted** - From show_phones API
- ✅ **One phone per row** - Easy data analysis
- ✅ **Crash-proof** - Auto-save checkpoints
- ✅ **Multi-format export** - JSON, CSV, XLSX
- ✅ **Comprehensive data** - 25+ fields per listing

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure credentials
Edit `.env` file with your Bright Data credentials.

### 3. Run scraper
```bash
python turbo_scraper_async.py
```

## Configuration

Edit `config.py` to adjust:
- `max_workers`: Concurrent requests (default: 15)
- `timeout`: Request timeout (default: 15s)
- Delays and retry settings

## Performance

**Test Results (5 pages):**
- Time: 1.53 minutes
- Speed: 1.79 listings/second
- Scraped: 164 listings → 220 rows (with phones expanded)

**Estimated for 1855 pages:**
- Time: **~9 hours 26 minutes**
- Listings: ~60,843

## Data Extracted

- ID, URL, Title, Price
- Brand, Model, Year
- City, Body type, Color
- Engine, Mileage, Transmission
- Phone numbers (separate rows)
- Images, Labels
- Owner info, Statistics
- And more...

## Files

- `turbo_scraper_async.py` - Main async scraper
- `config.py` - Configuration
- `.env` - Credentials (not in git)
- `test_async.py` - Test script for 5 pages

## Why Async?

The original ThreadPoolExecutor version had hanging issues. Async/aiohttp provides:
- Better timeout handling
- No thread deadlocks
- Faster concurrent execution
- Proper resource cleanup
