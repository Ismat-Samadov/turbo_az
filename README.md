# Turbo.az Car Scraper

High-performance async scraper for turbo.az with **automatic crash recovery**. Never lose data even if the scraper crashes, network fails, or you interrupt it.

## Key Features

- ⚡ **Async/Concurrent** - Fast scraping with aiohttp
- 💾 **Auto-Save** - Saves progress every 10 listings
- 🔄 **Crash Recovery** - Resume from where it stopped
- 📊 **Complete Data** - All car details, images, seller info
- 📁 **Multiple Formats** - CSV, Excel, JSON
- 🛡️ **Network Resilient** - Auto-retry on failures
- ⌨️ **Ctrl+C Safe** - Interrupt anytime, progress saved

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python turbo_scraper.py
```

That's it! The scraper will:
1. Scrape pages 1-5 (configurable)
2. Auto-save progress every 10 listings
3. Resume automatically if interrupted
4. Export to CSV, Excel, and JSON when done

## Configuration

Edit these settings in `turbo_scraper.py` (around line 545):

```python
START_PAGE = 1           # Start page
END_PAGE = 5            # End page
BASE_URL = "https://turbo.az/autos"  # Or add filters
MAX_CONCURRENT = 10     # Concurrent requests
DELAY = 0.5            # Delay between requests (seconds)
AUTO_SAVE_INTERVAL = 10 # Save every N listings
```

### Filter Examples

```python
# Mercedes only
BASE_URL = "https://turbo.az/autos?q[make][]=4"

# Price range 10k-30k AZN
BASE_URL = "https://turbo.az/autos?q[price_from]=10000&q[price_to]=30000"

# Year 2020-2024
BASE_URL = "https://turbo.az/autos?q[year_from]=2020&q[year_to]=2024"

# Multiple filters (Mercedes, 2020+, 20k-50k, Baku)
BASE_URL = "https://turbo.az/autos?q[make][]=4&q[year_from]=2020&q[price_from]=20000&q[price_to]=50000&q[region][]=1"
```

**Make IDs Reference:**
- BMW: 1, Hyundai: 2, LADA: 3, Mercedes: 4, Nissan: 5, Opel: 6
- Kia: 8, Ford: 9, Toyota: 11, Audi: 13, Chevrolet: 14, Honda: 15
- Mazda: 16, Mitsubishi: 17, Renault: 18, Volkswagen: 10
- Lexus: 23, Land Rover: 25, Jeep: 26

## Crash Recovery

The scraper automatically saves progress and can resume from interruptions:

### How It Works

1. **Auto-Checkpoints** - Saves after each page and every 10 listings
2. **Data Backup** - All scraped data saved to `scraped_data_backup.json`
3. **Smart Resume** - Skips already scraped URLs on restart

### Files Created

- `scraper_checkpoint.json` - Progress tracking
- `scraped_data_backup.json` - All scraped data
- `scraper.log` - Detailed logs

### Interruption Scenarios

**Network failure:**
- Scraper auto-retries 3 times with exponential backoff
- If still failing, saves progress and you can resume later

**Power outage / Crash:**
- Checkpoint files persist on disk
- Run script again - it resumes automatically

**User interruption (Ctrl+C):**
- Graceful shutdown, saves all progress
- Run again to continue

**Resume Example:**
```bash
# First run - interrupted after 50 listings
python turbo_scraper.py
# ... scrapes 50 listings ...
# Press Ctrl+C

# Second run - automatically resumes
python turbo_scraper.py
# "Resuming from checkpoint: 50 listings already scraped"
# Continues from listing 51...
```

## Data Collected

### Basic Information
- Listing ID, URL, Title, Price

### Car Details
- Make, Model, Year, Mileage
- Engine (volume, power, fuel type)
- Transmission, Drivetrain, Body Type
- Color, Seats, Condition, Market
- New/Used status

### Location & Seller
- City, Seller Name

### Additional
- Full Description
- Features/Extras
- View Count, Update Date
- VIP/Featured/Salon/Credit/Barter badges
- Up to 10 high-resolution images

## Output Files

After completion:
- `turbo_az_listings_YYYYMMDD_HHMMSS.csv`
- `turbo_az_listings_YYYYMMDD_HHMMSS.xlsx`
- `turbo_az_listings_YYYYMMDD_HHMMSS.json`

Checkpoint files are auto-deleted on successful completion.

## Performance

- ~50-100 listings/minute (default settings)
- Memory efficient
- Respectful rate limiting

### Adjust Speed

**Faster (use carefully):**
```python
MAX_CONCURRENT = 20
DELAY = 0.3
```

**More stable:**
```python
MAX_CONCURRENT = 5
DELAY = 1.0
```

## Troubleshooting

**Connection errors:**
- Increase `DELAY` to 1.0
- Decrease `MAX_CONCURRENT` to 5

**Scraper seems stuck:**
- Check `scraper.log` for details
- Network may be slow, be patient

**Want to start fresh:**
```bash
rm scraper_checkpoint.json scraped_data_backup.json
python turbo_scraper.py
```

## Data Analysis

```python
import pandas as pd

# Load data
df = pd.read_csv('turbo_az_listings_20251122_173045.csv')

# Average price by make
df['price_num'] = df['price_azn'].str.extract('(\d+)').astype(float)
print(df.groupby('make')['price_num'].mean().sort_values(ascending=False))

# Most common models
print(df['model'].value_counts().head(10))

# Price vs mileage
df['mileage_km'] = df['mileage'].str.extract('(\d+)').astype(float)
df.plot.scatter('mileage_km', 'price_num')
```

## Files in This Project

- `turbo_scraper.py` - Main scraper with crash recovery
- `requirements.txt` - Dependencies
- `README.md` - This file

## Notes

- Respects rate limits with configurable delays
- Scrapes only publicly available data
- For personal use and market research
- Use responsibly

## License

Educational and research purposes.

---

**Start scraping:** `python turbo_scraper.py`
