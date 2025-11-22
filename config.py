"""
Configuration file for Turbo.az scraper
Modify these settings according to your needs
"""

# Scraping Configuration
SCRAPER_CONFIG = {
    # Page range to scrape
    'start_page': 1,
    'end_page': 5,  # Increase this to scrape more pages

    # Base URL (you can add filters here)
    # Examples:
    # - All cars: "https://turbo.az/autos"
    # - Specific make: "https://turbo.az/autos?q[make][]=1" (1 = Mercedes, 8 = Kia, etc.)
    # - Price range: "https://turbo.az/autos?q[price_from]=10000&q[price_to]=50000"
    # - Year range: "https://turbo.az/autos?q[year_from]=2020&q[year_to]=2024"
    'base_url': "https://turbo.az/autos",

    # Request settings
    'max_concurrent_requests': 10,  # Number of simultaneous requests
    'delay_between_requests': 0.5,  # Delay in seconds (be respectful!)
    'request_timeout': 30,  # Timeout for each request in seconds
    'retry_count': 3,  # Number of retries for failed requests

    # Output settings
    'save_csv': True,
    'save_excel': True,
    'save_json': True,
    'output_dir': '.',  # Directory to save output files
}

# Search URL Examples (uncomment and use in your scraper)
SEARCH_EXAMPLES = {
    'all_cars': "https://turbo.az/autos",
    'mercedes_only': "https://turbo.az/autos?q[make][]=4",
    'kia_only': "https://turbo.az/autos?q[make][]=8",
    'toyota_only': "https://turbo.az/autos?q[make][]=11",
    'bmw_only': "https://turbo.az/autos?q[make][]=1",
    'price_10k_to_30k': "https://turbo.az/autos?q[price_from]=10000&q[price_to]=30000",
    'year_2020_to_2024': "https://turbo.az/autos?q[year_from]=2020&q[year_to]=2024",
    'new_cars_only': "https://turbo.az/autos?q[reg_new]=1",
    'baku_only': "https://turbo.az/autos?q[region][]=1",
    'automatic_transmission': "https://turbo.az/autos?q[transmission][]=1",
    'suv_only': "https://turbo.az/autos?q[category][]=2",
}

# User Agent (rotating user agents for better scraping)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
]

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR
    'log_file': 'scraper.log',
    'console_output': True,
}

# Make/Brand IDs (for reference when building URLs)
MAKE_IDS = {
    'bmw': 1,
    'hyundai': 2,
    'lada': 3,
    'mercedes': 4,
    'nissan': 5,
    'opel': 6,
    'toyota': 11,
    'kia': 8,
    'ford': 9,
    'volkswagen': 10,
    'audi': 13,
    'chevrolet': 14,
    'honda': 15,
    'mazda': 16,
    'mitsubishi': 17,
    'renault': 18,
    'skoda': 19,
    'subaru': 20,
    'suzuki': 21,
    'volvo': 22,
    'lexus': 23,
    'porsche': 24,
    'land_rover': 25,
    'jeep': 26,
    'acura': 27,
    'infiniti': 28,
    'cadillac': 29,
    'chrysler': 30,
}
