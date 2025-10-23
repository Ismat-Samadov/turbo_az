"""
Configuration for Turbo.az scraper
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bright Data Proxy Configuration
PROXY_CONFIG = {
    'enabled': True,
    'host': os.getenv('PROXY_HOST', 'brd.superproxy.io'),
    'port': int(os.getenv('PROXY_PORT', 33335)),
    'username': os.getenv('PROXY_USERNAME'),
    'password': os.getenv('PROXY_PASSWORD'),
    'zone': 'turboaz_mobile',
    'country': os.getenv('PROXY_COUNTRY', None),  # Optional: 'us', 'gb', 'az', etc. (leave None for any country)
    'ssl_cert': 'brightdata_proxy_ca/New SSL certifcate - MUST BE USED WITH PORT 33335/BrightData SSL certificate (port 33335).crt',
    'verify_ssl': True,  # SSL certificate required for port 33335
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'max_workers': 15,  # Number of concurrent workers
    'page_delay': 0.1,  # Delay between pages (seconds)
    'listing_delay': 0,  # Delay between listings (seconds)
    'timeout': 15,  # Request timeout (seconds)
    'retry_attempts': 1,  # Number of retries on failure
    'retry_delay': 0.5,  # Delay between retries (seconds)
}

# Checkpoint Configuration
CHECKPOINT_CONFIG = {
    'enabled': True,
    'file': 'scraper_checkpoint.json',
    'save_frequency': 1,  # Save after every N listings
}
