# Turbo.az Car Listings Scraper

A high-performance, asynchronous web scraper for turbo.az car listings built with Python, aiohttp, and asyncio. Designed for market analysis and data collection.

## Features

- ⚡ **Asynchronous scraping** using asyncio and aiohttp for maximum performance
- 📊 **Comprehensive data extraction** - captures all valuable car listing information
- 💾 **Multiple export formats** - CSV, Excel (XLSX), and JSON
- 🔄 **Automatic retry logic** with exponential backoff
- 📝 **Detailed logging** to track progress and errors
- 🛡️ **Respectful scraping** with configurable delays and rate limiting
- 🎯 **Flexible filtering** - scrape by make, model, price, year, location, etc.

## Data Collected

For each car listing, the scraper collects:

### Basic Information
- Listing ID and URL
- Title and Price (AZN)

### Car Details
- Make, Model, Year
- Mileage
- Engine: Volume, Power, Fuel Type
- Transmission Type
- Drivetrain (4WD, FWD, RWD)
- Body Type
- Color
- Number of Seats
- Condition
- Market (which market the car was built for)
- New/Used status

### Location & Seller
- City
- Seller Name
- Seller Contact Info

### Additional Information
- Full Description
- List of Extras/Features
- View Count
- Posted/Updated Dates

### Badges & Flags
- VIP Status
- Featured/Premium Status
- Salon (Dealership) Status
- Credit Available
- Barter Possible
- VIN Verified

### Media
- Image URLs (up to 10 images per listing)

### Metadata
- Scraping Timestamp

## Installation

1. **Clone or download this repository**

2. **Install required dependencies:**

```bash
pip install -r requirements.txt
```

Required packages:
- aiohttp >= 3.9.0
- beautifulsoup4 >= 4.12.0
- pandas >= 2.1.0
- openpyxl >= 3.1.0
- lxml >= 4.9.0

## Usage

### Basic Usage

Run the scraper with default settings (pages 1-3):

```bash
python turbo_scraper.py
```

### Advanced Configuration

Edit `config.py` to customize your scraping:

```python
SCRAPER_CONFIG = {
    'start_page': 1,
    'end_page': 10,  # Scrape pages 1-10
    'base_url': "https://turbo.az/autos",
    'max_concurrent_requests': 10,
    'delay_between_requests': 0.5,
}
```

### Custom Search Examples

#### Scrape specific car makes:

```python
# In turbo_scraper.py, modify BASE_URL in main():
BASE_URL = "https://turbo.az/autos?q[make][]=4"  # Mercedes only
BASE_URL = "https://turbo.az/autos?q[make][]=8"  # Kia only
```

#### Scrape by price range:

```python
BASE_URL = "https://turbo.az/autos?q[price_from]=10000&q[price_to]=30000"
```

#### Scrape by year:

```python
BASE_URL = "https://turbo.az/autos?q[year_from]=2020&q[year_to]=2024"
```

#### Combine multiple filters:

```python
# Mercedes cars, 2020-2024, in Baku, price 20k-50k
BASE_URL = "https://turbo.az/autos?q[make][]=4&q[year_from]=2020&q[year_to]=2024&q[region][]=1&q[price_from]=20000&q[price_to]=50000"
```

### Programmatic Usage

You can also use the scraper as a module:

```python
import asyncio
from turbo_scraper import TurboAzScraper

async def scrape_custom():
    async with TurboAzScraper(max_concurrent_requests=10, delay_between_requests=0.5) as scraper:
        # Scrape specific pages
        listings = await scraper.scrape_all_pages(
            start_page=1,
            end_page=5,
            base_search_url="https://turbo.az/autos?q[make][]=4"
        )

        # Save in your preferred format
        scraper.save_to_csv("mercedes_listings.csv")
        scraper.save_to_excel("mercedes_listings.xlsx")

        return listings

# Run the scraper
listings = asyncio.run(scrape_custom())
print(f"Scraped {len(listings)} listings")
```

## Output Files

The scraper generates three files with timestamps:

1. **CSV File**: `turbo_az_listings_YYYYMMDD_HHMMSS.csv`
   - Best for data analysis in Excel/Python/R
   - UTF-8 encoded with BOM for proper Azerbaijani character support

2. **Excel File**: `turbo_az_listings_YYYYMMDD_HHMMSS.xlsx`
   - Formatted with auto-adjusted column widths
   - Easy to share and view

3. **JSON File**: `turbo_az_listings_YYYYMMDD_HHMMSS.json`
   - Best for programmatic access
   - Preserves data structure

## Configuration Options

### Scraper Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `start_page` | First page to scrape | 1 |
| `end_page` | Last page to scrape | 3 |
| `max_concurrent_requests` | Number of simultaneous requests | 10 |
| `delay_between_requests` | Delay between requests (seconds) | 0.5 |
| `request_timeout` | Timeout for each request | 30 |
| `retry_count` | Number of retries for failed requests | 3 |

### Best Practices

1. **Be Respectful**: Use appropriate delays to avoid overwhelming the server
   - Recommended delay: 0.5-1 second
   - For large scrapes, consider 1-2 seconds

2. **Start Small**: Test with a few pages first
   ```python
   END_PAGE = 2  # Test with 2 pages
   ```

3. **Monitor Logs**: Check `scraper.log` for issues
   ```bash
   tail -f scraper.log  # On Linux/Mac
   type scraper.log     # On Windows
   ```

4. **Handle Rate Limiting**: If you get blocked:
   - Increase `delay_between_requests`
   - Decrease `max_concurrent_requests`
   - Add more user agents to rotation

## Performance

### Benchmarks
- ~50-100 listings per minute (with default settings)
- Memory efficient: streams data, doesn't load everything at once
- CPU: Uses async I/O, minimal CPU usage

### Optimization Tips

1. **Increase Concurrency** (if your connection can handle it):
   ```python
   max_concurrent_requests=20
   ```

2. **Decrease Delay** (use cautiously):
   ```python
   delay_between_requests=0.3
   ```

3. **Batch Processing**: Process pages in batches for very large scrapes

## Market Analysis Use Cases

This scraper is perfect for:

- 📈 **Price Analysis**: Track market prices for specific models
- 📊 **Market Trends**: Analyze supply/demand by make/model
- 🔍 **Inventory Monitoring**: Track dealership inventory
- 💰 **Investment Research**: Find undervalued listings
- 📉 **Depreciation Studies**: Compare prices across years
- 🌍 **Regional Analysis**: Compare prices across cities
- 📱 **Alert Systems**: Build notification systems for new listings

## Data Analysis Examples

### Load and analyze with pandas:

```python
import pandas as pd

# Load the data
df = pd.read_csv('turbo_az_listings_20250122_153045.csv')

# Average price by make
avg_price = df.groupby('make')['price_azn'].apply(
    lambda x: x.str.replace(' ₼', '').str.replace(' ', '').astype(float).mean()
)
print(avg_price)

# Most common car models
print(df['model'].value_counts().head(10))

# Average mileage by year
df['mileage_km'] = df['mileage'].str.extract('(\d+)').astype(float)
print(df.groupby('year')['mileage_km'].mean())
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Solution: Increase `delay_between_requests` and reduce `max_concurrent_requests`

2. **Missing Data**
   - Check `scraper.log` for parsing errors
   - Website HTML structure may have changed

3. **Encoding Issues**
   - CSV uses UTF-8 with BOM - should work with Excel
   - Use Excel's "Get Data" feature if characters look wrong

4. **Slow Performance**
   - Increase `max_concurrent_requests` if your connection allows
   - Check your internet connection speed

## Logging

Logs are saved to `scraper.log` and also printed to console.

Log levels:
- **INFO**: Progress updates, successful operations
- **WARNING**: Recoverable issues (e.g., failed to fetch a page)
- **ERROR**: Serious errors (e.g., parsing failures)

## Ethical Considerations

- 🤝 This scraper is for personal use and market research
- ⏱️ Respects rate limiting with configurable delays
- 📜 Scrapes only publicly available data
- 🚫 Does not bypass any authentication or paywalls
- 💡 Use responsibly and in accordance with turbo.az Terms of Service

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please:
1. Test your changes
2. Update documentation
3. Follow existing code style

## Support

For issues or questions:
1. Check `scraper.log` for error messages
2. Review this README
3. Check the code comments in `turbo_scraper.py`

## Changelog

### v1.0.0 (2025-01-22)
- Initial release
- Async scraping with aiohttp
- CSV, Excel, and JSON export
- Comprehensive data extraction
- Error handling and retry logic
- Configurable settings

---

**Happy Scraping! 🚗💨**
