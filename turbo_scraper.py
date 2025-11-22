"""
Turbo.az Car Listings Scraper
Asynchronously scrapes car listings from turbo.az for market analysis
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
import time
from dataclasses import dataclass, asdict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CarListing:
    """Data model for car listing"""
    # Basic Info
    listing_id: str = ""
    listing_url: str = ""
    title: str = ""
    price_azn: str = ""

    # Car Details
    make: str = ""
    model: str = ""
    year: str = ""
    mileage: str = ""
    engine_volume: str = ""
    engine_power: str = ""
    fuel_type: str = ""

    # Technical Specs
    transmission: str = ""
    drivetrain: str = ""
    body_type: str = ""
    color: str = ""
    seats_count: str = ""
    condition: str = ""
    market: str = ""
    is_new: str = ""

    # Location & Seller
    city: str = ""
    seller_name: str = ""
    seller_phone: str = ""

    # Additional Info
    description: str = ""
    extras: str = ""
    views: str = ""
    updated_date: str = ""
    posted_date: str = ""

    # Badges/Flags
    is_vip: bool = False
    is_featured: bool = False
    is_salon: bool = False
    has_credit: bool = False
    has_barter: bool = False
    has_vin: bool = False

    # Images
    image_urls: str = ""

    # Metadata
    scraped_at: str = ""


class TurboAzScraper:
    """Asynchronous scraper for turbo.az car listings"""

    def __init__(self, max_concurrent_requests: int = 10, delay_between_requests: float = 0.5):
        self.base_url = "https://turbo.az"
        self.max_concurrent_requests = max_concurrent_requests
        self.delay_between_requests = delay_between_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None
        self.scraped_listings = []

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'az,en-US;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str, retry_count: int = 3) -> Optional[str]:
        """Fetch a single page with retry logic"""
        async with self.semaphore:
            for attempt in range(retry_count):
                try:
                    await asyncio.sleep(self.delay_between_requests)
                    async with self.session.get(url, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            logger.warning(f"Failed to fetch {url}: Status {response.status}")
                except Exception as e:
                    logger.error(f"Error fetching {url} (attempt {attempt + 1}/{retry_count}): {e}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            return None

    def extract_listing_urls(self, html: str) -> List[str]:
        """Extract all car listing URLs from a page"""
        soup = BeautifulSoup(html, 'html.parser')
        listing_urls = []

        # Find all product items
        products = soup.find_all('div', class_='products-i')

        for product in products:
            link = product.find('a', class_='products-i__link')
            if link and link.get('href'):
                full_url = urljoin(self.base_url, link['href'])
                listing_urls.append(full_url)

        logger.info(f"Found {len(listing_urls)} listings on page")
        return listing_urls

    def extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        match = re.search(r'/autos/(\d+)', url)
        return match.group(1) if match else ""

    def clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

    def parse_listing_page(self, html: str, url: str) -> CarListing:
        """Parse individual car listing page"""
        soup = BeautifulSoup(html, 'html.parser')
        listing = CarListing()

        # Basic info
        listing.listing_id = self.extract_listing_id(url)
        listing.listing_url = url
        listing.scraped_at = datetime.now().isoformat()

        # Extract title
        title_elem = soup.find('h1', class_='product-title')
        if title_elem:
            listing.title = self.clean_text(title_elem.get_text())

        # Extract price
        price_elem = soup.find('div', class_='product-price__i--bold')
        if price_elem:
            listing.price_azn = self.clean_text(price_elem.get_text())

        # Extract properties
        properties = soup.find_all('div', class_='product-properties__i')
        for prop in properties:
            label_elem = prop.find('label', class_='product-properties__i-name')
            value_elem = prop.find('span', class_='product-properties__i-value')

            if not label_elem or not value_elem:
                continue

            label = self.clean_text(label_elem.get_text())
            value = self.clean_text(value_elem.get_text())

            # Map properties to listing fields
            if 'Şəhər' in label or 'City' in label:
                listing.city = value
            elif 'Marka' in label or 'Make' in label:
                listing.make = value
            elif 'Model' in label:
                listing.model = value
            elif 'Buraxılış ili' in label or 'year' in label.lower():
                listing.year = value
            elif 'Yürüş' in label or 'Mileage' in label:
                listing.mileage = value
            elif 'Mühərrik' in label or 'Engine' in label:
                # Parse engine info: "2.5 L / 174 a.g. / Dizel"
                engine_parts = value.split('/')
                if len(engine_parts) >= 1:
                    listing.engine_volume = self.clean_text(engine_parts[0])
                if len(engine_parts) >= 2:
                    listing.engine_power = self.clean_text(engine_parts[1])
                if len(engine_parts) >= 3:
                    listing.fuel_type = self.clean_text(engine_parts[2])
            elif 'Sürətlər qutusu' in label or 'Transmission' in label:
                listing.transmission = value
            elif 'Ötürücü' in label or 'Drivetrain' in label:
                listing.drivetrain = value
            elif 'Ban növü' in label or 'Body' in label:
                listing.body_type = value
            elif 'Rəng' in label or 'Color' in label:
                listing.color = value
            elif 'Yerlərin sayı' in label or 'Seats' in label:
                listing.seats_count = value
            elif 'Vəziyyəti' in label or 'Condition' in label:
                listing.condition = value
            elif 'bazar üçün yığılıb' in label or 'Market' in label:
                listing.market = value
            elif 'Yeni' in label or 'New' in label:
                listing.is_new = value

        # Extract description
        desc_elem = soup.find('div', class_='product-description__content')
        if desc_elem:
            listing.description = self.clean_text(desc_elem.get_text())

        # Extract extras/features
        extras_list = soup.find('ul', class_='product-extras')
        if extras_list:
            extras = [self.clean_text(li.get_text()) for li in extras_list.find_all('li')]
            listing.extras = ' | '.join(extras)

        # Extract seller info
        seller_name_elem = soup.find('div', class_='product-owner__info-name')
        if seller_name_elem:
            listing.seller_name = self.clean_text(seller_name_elem.get_text())

        # Extract statistics
        stats = soup.find('ul', class_='product-statistics')
        if stats:
            for stat in stats.find_all('li'):
                text = self.clean_text(stat.get_text())
                if 'Yeniləndi' in text or 'Updated' in text:
                    listing.updated_date = text.replace('Yeniləndi:', '').strip()
                elif 'Baxışların sayı' in text or 'Views' in text:
                    match = re.search(r'\d+', text)
                    if match:
                        listing.views = match.group()

        # Extract badges/flags from main page context
        # Check for VIP, Featured, Salon badges
        if soup.find('span', class_='vipped-icon'):
            listing.is_vip = True
        if soup.find('span', class_='featured-icon'):
            listing.is_featured = True
        if soup.find('div', class_='products-i__label--salon'):
            listing.is_salon = True

        # Check for credit/barter icons
        if soup.find('div', class_='products-i__icon--loan'):
            listing.has_credit = True
        if soup.find('div', class_='products-i__icon--barter'):
            listing.has_barter = True
        if soup.find('div', class_='products-i__label--vin'):
            listing.has_vin = True

        # Extract image URLs
        image_urls = []
        slider_images = soup.find_all('img', alt=re.compile(r'.*'))
        for img in slider_images:
            src = img.get('src')
            if src and 'turbo.azstatic.com' in src and 'uploads' in src:
                # Get full resolution image
                full_img = src.replace('f460x343', 'full').replace('f660x496', 'full')
                if full_img not in image_urls:
                    image_urls.append(full_img)

        listing.image_urls = ' | '.join(image_urls[:10])  # Limit to first 10 images

        return listing

    async def scrape_listing(self, url: str) -> Optional[CarListing]:
        """Scrape a single car listing"""
        logger.info(f"Scraping listing: {url}")

        html = await self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch listing: {url}")
            return None

        try:
            listing = self.parse_listing_page(html, url)
            logger.info(f"Successfully scraped listing {listing.listing_id}: {listing.title}")
            return listing
        except Exception as e:
            logger.error(f"Error parsing listing {url}: {e}")
            return None

    async def scrape_page(self, page_num: int, base_search_url: str = None) -> List[str]:
        """Scrape all listing URLs from a single page"""
        if base_search_url is None:
            base_search_url = f"{self.base_url}/autos"

        url = f"{base_search_url}?page={page_num}" if page_num > 1 else base_search_url
        logger.info(f"Scraping page {page_num}: {url}")

        html = await self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch page {page_num}")
            return []

        return self.extract_listing_urls(html)

    async def scrape_all_pages(self, start_page: int = 1, end_page: int = 10,
                               base_search_url: str = None) -> List[CarListing]:
        """Scrape all pages and their listings"""
        all_listing_urls = []

        # Step 1: Collect all listing URLs from all pages
        logger.info(f"Collecting listing URLs from pages {start_page} to {end_page}")
        page_tasks = [
            self.scrape_page(page_num, base_search_url)
            for page_num in range(start_page, end_page + 1)
        ]

        page_results = await asyncio.gather(*page_tasks)
        for urls in page_results:
            all_listing_urls.extend(urls)

        # Remove duplicates
        all_listing_urls = list(set(all_listing_urls))
        logger.info(f"Found {len(all_listing_urls)} unique listings")

        # Step 2: Scrape all individual listings
        logger.info("Starting to scrape individual listings...")
        listing_tasks = [self.scrape_listing(url) for url in all_listing_urls]

        listings = await asyncio.gather(*listing_tasks)

        # Filter out None results
        valid_listings = [l for l in listings if l is not None]
        logger.info(f"Successfully scraped {len(valid_listings)} out of {len(all_listing_urls)} listings")

        self.scraped_listings = valid_listings
        return valid_listings

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV"""
        if not self.scraped_listings:
            logger.warning("No listings to save")
            return

        if filename is None:
            filename = f"turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Convert to DataFrame
        data = [asdict(listing) for listing in self.scraped_listings]
        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"Saved {len(self.scraped_listings)} listings to {filename}")

    def save_to_excel(self, filename: str = None):
        """Save scraped data to Excel"""
        if not self.scraped_listings:
            logger.warning("No listings to save")
            return

        if filename is None:
            filename = f"turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # Convert to DataFrame
        data = [asdict(listing) for listing in self.scraped_listings]
        df = pd.DataFrame(data)

        # Save to Excel with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Listings', index=False)

            # Auto-adjust column widths
            from openpyxl.utils import get_column_letter
            worksheet = writer.sheets['Listings']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                col_letter = get_column_letter(idx + 1)
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)

        logger.info(f"Saved {len(self.scraped_listings)} listings to {filename}")

    def save_to_json(self, filename: str = None):
        """Save scraped data to JSON"""
        if not self.scraped_listings:
            logger.warning("No listings to save")
            return

        if filename is None:
            filename = f"turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convert to dict
        data = [asdict(listing) for listing in self.scraped_listings]

        # Save to JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(self.scraped_listings)} listings to {filename}")


async def main():
    """Main execution function"""

    # Configuration
    START_PAGE = 1
    END_PAGE = 3  # Adjust this to scrape more pages
    BASE_URL = "https://turbo.az/autos"  # Can customize with filters
    MAX_CONCURRENT = 10  # Number of concurrent requests
    DELAY = 0.5  # Delay between requests in seconds

    logger.info("Starting Turbo.az scraper...")
    logger.info(f"Pages to scrape: {START_PAGE} to {END_PAGE}")
    logger.info(f"Max concurrent requests: {MAX_CONCURRENT}")
    logger.info(f"Delay between requests: {DELAY}s")

    start_time = time.time()

    async with TurboAzScraper(
        max_concurrent_requests=MAX_CONCURRENT,
        delay_between_requests=DELAY
    ) as scraper:
        # Scrape all pages
        listings = await scraper.scrape_all_pages(
            start_page=START_PAGE,
            end_page=END_PAGE,
            base_search_url=BASE_URL
        )

        # Save results in multiple formats
        scraper.save_to_csv()
        scraper.save_to_excel()
        scraper.save_to_json()

    elapsed_time = time.time() - start_time
    logger.info(f"Scraping completed in {elapsed_time:.2f} seconds")
    logger.info(f"Total listings scraped: {len(listings)}")
    logger.info(f"Average time per listing: {elapsed_time/len(listings):.2f}s" if listings else "N/A")


if __name__ == "__main__":
    asyncio.run(main())
