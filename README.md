# Turbo.az Car Scraper & Market Analysis

High-performance async scraper for turbo.az with **automatic crash recovery** and comprehensive **market analysis tools**. Never lose data even if the scraper crashes, network fails, or you interrupt it.

---

## Key Features

### Scraper
- ⚡ **Async/Concurrent** - Fast scraping with aiohttp
- 💾 **Auto-Save** - Saves progress every 10 listings
- 🔄 **Crash Recovery** - Resume from where it stopped
- 📊 **Complete Data** - All car details, images, seller info
- 📁 **Multiple Formats** - CSV, Excel, JSON
- 🛡️ **Network Resilient** - Auto-retry on failures
- ⌨️ **Ctrl+C Safe** - Interrupt anytime, progress saved
- 🎯 **Smart Deduplication** - Removes duplicate listings by ID

### Analysis
- 📈 **14 Professional Charts** - High-resolution visualizations
- 🎯 **Actionable Insights** - Buying/selling recommendations
- 💡 **Market Trends** - Price patterns, brand analysis, segments
- 📊 **Statistical Analysis** - Distribution, correlations, segments

---

## Installation

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- aiohttp, beautifulsoup4, pandas, matplotlib, seaborn, openpyxl

---

## Quick Start

### 1. Scrape Data

```bash
python turbo_scraper.py
```

The scraper will:
1. Scrape pages 1-185 (configurable)
2. Auto-save progress every 10 listings
3. Resume automatically if interrupted
4. Export to CSV, Excel, and JSON when done

### 2. Generate Analysis

Data analysis charts are generated during scraping. View the comprehensive report:

**[📊 View Full Market Analysis Report](charts/README.md)**

---

## Configuration

Edit settings in `turbo_scraper.py` (around line 569):

```python
START_PAGE = 1           # Start page
END_PAGE = 185          # End page (current: scrape all pages)
BASE_URL = "https://turbo.az/autos"  # Or add filters
MAX_CONCURRENT = 10     # Concurrent requests
DELAY = 0              # Delay between requests (seconds)
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

---

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

---

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
- VIP/Featured/Salon/Credit/Barter/VIN badges
- Up to 10 high-resolution images

---

## Output Files

After completion:
- `turbo_az_listings_YYYYMMDD_HHMMSS.csv`
- `turbo_az_listings_YYYYMMDD_HHMMSS.xlsx`
- `turbo_az_listings_YYYYMMDD_HHMMSS.json`

Combined/deduplicated:
- `turbo_az_listings_combined_YYYYMMDD_HHMMSS.csv`

Checkpoint files are auto-deleted on successful completion.

---

## Data Analysis & Market Insights

Comprehensive market analysis with **14 professional charts** and **actionable insights**.

### Quick Analysis

```python
import pandas as pd

# Load data
df = pd.read_csv('turbo_az_listings_combined_YYYYMMDD_HHMMSS.csv')

# Average price by make
df['price_num'] = df['price_azn'].str.extract('(\d+)').astype(float)
print(df.groupby('make')['price_num'].mean().sort_values(ascending=False))

# Most common models
print(df['model'].value_counts().head(10))

# Price vs mileage
df['mileage_km'] = df['mileage'].str.extract('(\d+)').astype(float)
df.plot.scatter('mileage_km', 'price_num')
```

### Professional Market Analysis

**📊 [View Full Market Analysis Report](charts/README.md)**

The comprehensive analysis includes:

#### Price Analysis
- Price distribution and ranges
- Premium vs budget segments
- Average prices by brand
- Price depreciation patterns

#### Brand & Model Insights
- Top 15 makes and models
- Market share analysis
- Luxury vs volume brands
- Brand value retention

#### Market Trends
- Year distribution analysis
- New vs used car split
- Geographic concentration
- Seasonal patterns

#### Vehicle Analytics
- Fuel type distribution
- Transmission preferences
- Body type popularity
- Mileage vs price correlation

#### Actionable Insights
- **For Buyers:** Recommendations by budget segment
- **For Sellers:** Pricing strategies and timing
- **Investment:** Best value retention models
- **Market Predictions:** Growing and declining segments

### 14 Professional Charts

All charts are high-resolution (300 DPI) PNG files:

1. **Price Distribution** - Market pricing overview
2. **Top 15 Car Brands** - Most listed manufacturers
3. **Top 15 Models** - Bestselling car models
4. **Year Distribution** - Age of vehicles in market
5. **Average Price by Make** - Premium brand analysis
6. **Mileage vs Price** - Depreciation correlation
7. **Fuel Type Distribution** - Energy source breakdown
8. **Transmission Types** - Manual vs automatic preference
9. **Body Types** - Sedan, SUV, hatchback distribution
10. **New vs Used** - Market segment split
11. **Top Cities** - Geographic distribution
12. **Listing Features** - VIP, Salon, Credit, Barter badges
13. **Price Range Analysis** - Market segmentation
14. **Market Summary** - Key statistics overview

---

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

---

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

**Regenerate charts:**
```bash
python create_charts.py
```

---

## Files in This Project

### Core Files
- `turbo_scraper.py` - Main scraper with crash recovery
- `requirements.txt` - Python dependencies
- `README.md` - This file

### Analysis
- `create_charts.py` - Chart generation script
- `charts/` - Folder containing 14 analysis charts
- `charts/README.md` - Comprehensive market analysis report

### Data (Generated)
- `*.csv` - Scraped data in CSV format
- `*.xlsx` - Scraped data in Excel format
- `*.json` - Scraped data in JSON format
- `scraper.log` - Detailed execution logs

---

## Project Structure

```
turbo_az/
├── turbo_scraper.py              # Main scraper
├── create_charts.py              # Analysis script
├── requirements.txt              # Dependencies
├── README.md                     # This file
├── charts/                       # Analysis charts
│   ├── README.md                 # Market analysis report
│   ├── 01_price_distribution.png
│   ├── 02_top_makes.png
│   ├── 03_top_models.png
│   ├── 04_year_distribution.png
│   ├── 05_avg_price_by_make.png
│   ├── 06_mileage_vs_price.png
│   ├── 07_fuel_type_distribution.png
│   ├── 08_transmission_distribution.png
│   ├── 09_body_type_distribution.png
│   ├── 10_new_vs_used.png
│   ├── 11_top_cities.png
│   ├── 12_listing_features.png
│   ├── 13_price_ranges.png
│   └── 14_market_summary.png
└── turbo_az_listings_combined_*.csv  # Combined data
```

---

## Use Cases

### Market Research
- Identify pricing trends
- Analyze brand preferences
- Study market segmentation
- Track inventory patterns

### Buying Decisions
- Find fair market prices
- Compare similar vehicles
- Identify best value segments
- Time purchases strategically

### Selling Strategy
- Price competitively
- Highlight unique features
- Choose optimal timing
- Target right buyer segment

### Investment Analysis
- Identify value retention
- Predict depreciation
- Analyze market trends
- Portfolio optimization

---

## Notes

- Respects rate limits with configurable delays
- Scrapes only publicly available data
- For personal use and market research
- Use responsibly and ethically

---

## License

Educational and research purposes.

---

## Quick Commands

```bash
# Start scraping
python turbo_scraper.py

# Generate analysis charts
python create_charts.py

# View market report
cat charts/README.md
# Or open charts/README.md in browser
```

---

**📊 [View Comprehensive Market Analysis Report](charts/README.md)**

*Built with Python • Powered by aiohttp, BeautifulSoup, pandas, matplotlib*

