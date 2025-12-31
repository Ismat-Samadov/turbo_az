"""
Turbo.az Car Listings Scraper with Crash Recovery
Asynchronously scrapes car listings from turbo.az for market analysis
Features: Auto-save, checkpoint system, resume on crash/interruption
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional, Set
import re
from datetime import datetime
import logging
from urllib.parse import urljoin
import time
from dataclasses import dataclass, asdict
import json
import os
import signal
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
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


class CheckpointManager:
    """Manages scraping progress and crash recovery"""

    def __init__(self, checkpoint_file: str = "scraper_checkpoint.json"):
        self.checkpoint_file = checkpoint_file
        self.data_file = "scraped_data_backup.json"

    def save_checkpoint(self, scraped_urls: Set[str], pending_urls: List[str],
                       listings: List[CarListing], pages_completed: List[int]):
        """Save current progress"""
        checkpoint = {
            'scraped_urls': list(scraped_urls),
            'pending_urls': pending_urls,
            'pages_completed': pages_completed,
            'timestamp': datetime.now().isoformat(),
            'total_scraped': len(listings)
        }

        # Save checkpoint
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2)

        # Save data backup
        if listings:
            data = [asdict(listing) for listing in listings]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Checkpoint saved: {len(scraped_urls)} URLs scraped, {len(pending_urls)} pending")

    def load_checkpoint(self) -> Optional[Dict]:
        """Load previous progress if exists"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                logger.info(f"Resuming from checkpoint: {checkpoint['total_scraped']} listings already scraped")
                return checkpoint
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}")
                return None
        return None

    def load_data_backup(self) -> List[CarListing]:
        """Load previously scraped data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                listings = [CarListing(**item) for item in data]
                logger.info(f"Loaded {len(listings)} previously scraped listings")
                return listings
            except Exception as e:
                logger.error(f"Failed to load data backup: {e}")
                return []
        return []

    def clear_checkpoint(self):
        """Clear checkpoint files after successful completion"""
        for file in [self.checkpoint_file, self.data_file]:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"Removed {file}")


class TurboAzScraper:
    """Asynchronous scraper for turbo.az car listings with crash recovery"""

    def __init__(self, max_concurrent_requests: int = 10, delay_between_requests: float = 0.5, proxy_url = None):
        self.base_url = "https://turbo.az"
        self.max_concurrent_requests = max_concurrent_requests
        self.delay_between_requests = delay_between_requests

        # Support both single proxy URL and list of proxy URLs for rotation
        if isinstance(proxy_url, list):
            self.proxy_urls = proxy_url
            self.proxy_rotation_enabled = True
            self.current_proxy_index = 0
        elif proxy_url:
            self.proxy_urls = [proxy_url]
            self.proxy_rotation_enabled = False
            self.current_proxy_index = 0
        else:
            self.proxy_urls = []
            self.proxy_rotation_enabled = False
            self.current_proxy_index = 0

        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session = None
        self.scraped_listings = []
        self.checkpoint_manager = CheckpointManager()
        self.scraped_urls: Set[str] = set()
        self.should_stop = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interruption signals gracefully"""
        logger.warning("\nInterruption received! Saving progress...")
        self.should_stop = True

    def _get_current_proxy(self) -> Optional[str]:
        """Get the current proxy URL"""
        if not self.proxy_urls:
            return None
        return self.proxy_urls[self.current_proxy_index]

    def _rotate_proxy(self):
        """Rotate to the next proxy in the list"""
        if not self.proxy_rotation_enabled or len(self.proxy_urls) <= 1:
            return

        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_urls)
        safe_proxy = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', self._get_current_proxy())
        logger.info(f"Rotated to proxy: {safe_proxy}")

    async def __aenter__(self):
        """Async context manager entry"""
        # Log proxy usage
        if self.proxy_urls:
            if self.proxy_rotation_enabled and len(self.proxy_urls) > 1:
                logger.info(f"Proxy rotation enabled with {len(self.proxy_urls)} proxies")
                safe_proxy = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', self._get_current_proxy())
                logger.info(f"Starting with proxy: {safe_proxy}")
            else:
                safe_proxy = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', self._get_current_proxy())
                logger.info(f"Using proxy: {safe_proxy}")
        else:
            logger.info("No proxy configured - using direct connection")

        # Create SSL context that doesn't verify certificates
        # This is needed when there are SSL issues (corporate proxy, certificate problems)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        # Create cookie jar to maintain session cookies for AJAX requests
        cookie_jar = aiohttp.CookieJar()

        self.session = aiohttp.ClientSession(
            connector=connector,
            cookie_jar=cookie_jar,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'az,en-US;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str, retry_count: int = 3) -> Optional[str]:
        """Fetch a single page with retry logic, proxy rotation, and error handling"""
        async with self.semaphore:
            for attempt in range(retry_count):
                try:
                    await asyncio.sleep(self.delay_between_requests)
                    # Use current proxy if configured
                    current_proxy = self._get_current_proxy()
                    async with self.session.get(url, proxy=current_proxy) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 403 or response.status == 429:
                            # Rotate proxy on 403 (Forbidden) or 429 (Too Many Requests)
                            logger.warning(f"Status {response.status} on {url}, rotating proxy...")
                            self._rotate_proxy()
                        else:
                            logger.warning(f"Failed to fetch {url}: Status {response.status}")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{retry_count})")
                    self._rotate_proxy()  # Rotate on timeout
                except aiohttp.ClientError as e:
                    logger.warning(f"Network error fetching {url}: {e} (attempt {attempt + 1}/{retry_count})")
                    self._rotate_proxy()  # Rotate on network error
                except Exception as e:
                    logger.error(f"Error fetching {url}: {e} (attempt {attempt + 1}/{retry_count})")

                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            logger.error(f"Failed to fetch {url} after {retry_count} attempts")
            return None

    def extract_listing_urls(self, html: str) -> List[Dict[str, any]]:
        """Extract car listing URLs from the 'ELANLAR' section only (excluding promoted sections)"""
        soup = BeautifulSoup(html, 'html.parser')
        listing_data = []

        # Find the "ELANLAR" section title
        # There are 3 sections on each page:
        # 1. "SALONLARIN VIP ELANLARI" (skip)
        # 2. "VIP ELANLAR" (skip)
        # 3. "ELANLAR" (we want this one!)

        elanlar_section = None
        section_titles = soup.find_all('div', class_='section-title')

        for section in section_titles:
            title_elem = section.find('p', class_='section-title_name')
            if title_elem and 'ELANLAR' in title_elem.get_text() and 'VIP' not in title_elem.get_text():
                # Found the "ELANLAR" section (not "VIP ELANLAR")
                # The products container comes after this section title
                elanlar_section = section
                break

        if elanlar_section:
            # Find the products container that comes after the "ELANLAR" title
            # Navigate to the next sibling container that has products
            next_container = elanlar_section.find_next_sibling('div', class_='tz-container')
            if next_container:
                products_container = next_container.find('div', class_='products')
                if products_container:
                    products = products_container.find_all('div', class_='products-i')
                else:
                    products = []
            else:
                products = []
        else:
            # Fallback: if section structure not found, get all products (old behavior)
            logger.warning("Could not find 'ELANLAR' section, falling back to all products")
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

        logger.debug(f"Found {len(listing_data)} listings in 'ELANLAR' section")

        return listing_data

    def extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        match = re.search(r'/autos/(\d+)', url)
        return match.group(1) if match else ""

    def clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

    def extract_csrf_token(self, html: str) -> Optional[str]:
        """Extract CSRF token from HTML for AJAX requests"""
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find CSRF token in meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta and csrf_meta.get('content'):
            return csrf_meta.get('content')

        # Try to find in form input
        csrf_input = soup.find('input', {'name': 'authenticity_token'})
        if csrf_input and csrf_input.get('value'):
            return csrf_input.get('value')

        # Try to find in JavaScript/page source
        match = re.search(r'"authenticity_token"\s*value="([^"]+)"', html)
        if match:
            return match.group(1)

        match = re.search(r'authenticity_token.*?value="([^"]+)"', html)
        if match:
            return match.group(1)

        return None

    async def fetch_phone_numbers(self, listing_id: str, listing_url: str, csrf_token: Optional[str] = None) -> str:
        """Fetch phone numbers via AJAX endpoint"""
        from urllib.parse import quote

        # Build the show_phones URL
        encoded_url = quote(listing_url, safe='')
        phone_url = f"{self.base_url}/autos/{listing_id}/show_phones?trigger_button=main&source_link={encoded_url}"

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': listing_url,
        }

        # Add CSRF token if available
        if csrf_token:
            headers['X-CSRF-Token'] = csrf_token

        try:
            async with self.semaphore:
                await asyncio.sleep(self.delay_between_requests)
                # Use current proxy if configured
                current_proxy = self._get_current_proxy()
                async with self.session.get(phone_url, headers=headers, proxy=current_proxy) as response:
                    if response.status == 200:
                        data = await response.json()
                        phones = data.get('phones', [])
                        if phones:
                            # Extract primary formatted phone numbers
                            phone_list = [phone.get('primary', phone.get('raw', '')) for phone in phones]
                            return ' | '.join(phone_list)
                    else:
                        logger.warning(f"Failed to fetch phones for {listing_id}: Status {response.status}")
        except Exception as e:
            logger.warning(f"Error fetching phones for {listing_id}: {e}")

        return ""

    def parse_listing_page(self, html: str, url: str, badges: Dict[str, bool] = None) -> CarListing:
        """Parse individual car listing page"""
        soup = BeautifulSoup(html, 'html.parser')
        listing = CarListing()

        listing.listing_id = self.extract_listing_id(url)
        listing.listing_url = url
        listing.scraped_at = datetime.now().isoformat()

        # Set badges from listing card data
        if badges:
            listing.is_vip = badges.get('is_vip', False)
            listing.is_featured = badges.get('is_featured', False)
            listing.is_salon = badges.get('is_salon', False)
            listing.has_credit = badges.get('has_credit', False)
            listing.has_barter = badges.get('has_barter', False)
            listing.has_vin = badges.get('has_vin', False)

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

        # Extract extras
        extras_list = soup.find('ul', class_='product-extras')
        if extras_list:
            extras = [self.clean_text(li.get_text()) for li in extras_list.find_all('li')]
            listing.extras = ' | '.join(extras)

        # Extract seller info
        seller_name_elem = soup.find('div', class_='product-owner__info-name')
        if seller_name_elem:
            listing.seller_name = self.clean_text(seller_name_elem.get_text())

        # Extract posted date from shop-contact section
        shop_contact = soup.find('div', class_='shop-contact')
        if shop_contact:
            for item in shop_contact.find_all('div', class_='shop-contact__param'):
                label = item.find('div', class_='shop-contact__param-name')
                value = item.find('a', class_='shop-contact__param-value')
                if not value:
                    value = item.find('div', class_='shop-contact__param-value')

                if label and value:
                    label_text = self.clean_text(label.get_text())
                    if 'Turbo.az-da' in label_text or 'turbo.az-da' in label_text.lower():
                        listing.posted_date = self.clean_text(value.get_text())

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

        # Extract images
        image_urls = []
        slider_images = soup.find_all('img', alt=re.compile(r'.*'))
        for img in slider_images:
            src = img.get('src')
            if src and 'turbo.azstatic.com' in src and 'uploads' in src:
                full_img = src.replace('f460x343', 'full').replace('f660x496', 'full')
                if full_img not in image_urls:
                    image_urls.append(full_img)

        listing.image_urls = ' | '.join(image_urls[:10])

        return listing

    async def scrape_listing(self, url: str, badges: Dict[str, bool] = None) -> Optional[CarListing]:
        """Scrape a single car listing"""
        if self.should_stop:
            return None

        logger.info(f"Scraping: {url}")

        html = await self.fetch_page(url)
        if not html:
            return None

        try:
            listing = self.parse_listing_page(html, url, badges)

            # Extract phone numbers via AJAX endpoint
            if listing.listing_id:
                csrf_token = self.extract_csrf_token(html)
                phone_numbers = await self.fetch_phone_numbers(listing.listing_id, url, csrf_token)
                if phone_numbers:
                    listing.seller_phone = phone_numbers
                    logger.info(f"[PHONE] {listing.listing_id}: {phone_numbers}")
                else:
                    logger.debug(f"[NO PHONE] {listing.listing_id}")

            self.scraped_urls.add(url)
            logger.info(f"[OK] {listing.listing_id}: {listing.title}")
            return listing
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            return None

    async def scrape_page(self, page_num: int, base_search_url: str = None) -> List[Dict[str, any]]:
        """Scrape all listing URLs and badge data from a single page"""
        if base_search_url is None:
            base_search_url = f"{self.base_url}/autos"

        url = f"{base_search_url}?page={page_num}" if page_num > 1 else base_search_url
        logger.info(f"Fetching page {page_num}: {url}")

        html = await self.fetch_page(url)
        if not html:
            return []

        listing_data = self.extract_listing_urls(html)
        logger.info(f"Found {len(listing_data)} listings on page {page_num}")
        return listing_data

    async def scrape_all_pages(self, start_page: int = 1, end_page: int = 10,
                               base_search_url: str = None, auto_save_interval: int = 10) -> List[CarListing]:
        """Scrape all pages with crash recovery"""

        # Try to load previous progress
        checkpoint = self.checkpoint_manager.load_checkpoint()
        if checkpoint:
            self.scraped_urls = set(checkpoint.get('scraped_urls', []))
            pending_data = checkpoint.get('pending_urls', [])
            pages_completed = set(checkpoint.get('pages_completed', []))
            self.scraped_listings = self.checkpoint_manager.load_data_backup()
            logger.info(f"Resuming: {len(self.scraped_listings)} listings, {len(pending_data)} URLs pending")
        else:
            pending_data = []
            pages_completed = set()

        # Collect listing data from pages
        all_listing_data = list(pending_data)  # Start with pending data

        for page_num in range(start_page, end_page + 1):
            if self.should_stop:
                break

            if page_num in pages_completed:
                logger.info(f"Page {page_num} already processed, skipping")
                continue

            listing_data = await self.scrape_page(page_num, base_search_url)
            all_listing_data.extend(listing_data)
            pages_completed.add(page_num)

            # Save checkpoint after each page
            self.checkpoint_manager.save_checkpoint(
                self.scraped_urls,
                all_listing_data,
                self.scraped_listings,
                list(pages_completed)
            )

        # Remove already scraped URLs
        data_to_scrape = [item for item in all_listing_data if item['url'] not in self.scraped_urls]
        logger.info(f"Total URLs to scrape: {len(data_to_scrape)} (skipping {len(all_listing_data) - len(data_to_scrape)} already scraped)")

        # Scrape individual listings with auto-save
        for idx, item in enumerate(data_to_scrape, 1):
            if self.should_stop:
                logger.warning("Stopping due to interruption...")
                break

            listing = await self.scrape_listing(item['url'], item['badges'])
            if listing:
                self.scraped_listings.append(listing)

            # Auto-save every N listings
            if idx % auto_save_interval == 0:
                remaining_data = data_to_scrape[idx:]
                self.checkpoint_manager.save_checkpoint(
                    self.scraped_urls,
                    remaining_data,
                    self.scraped_listings,
                    list(pages_completed)
                )
                logger.info(f"Progress: {idx}/{len(data_to_scrape)} listings")

        # Final save
        if not self.should_stop:
            logger.info(f"Scraping completed! Total: {len(self.scraped_listings)} listings")
            # Clear checkpoint on successful completion
            self.checkpoint_manager.clear_checkpoint()
        else:
            # Save final checkpoint if interrupted
            self.checkpoint_manager.save_checkpoint(
                self.scraped_urls,
                [],
                self.scraped_listings,
                list(pages_completed)
            )
            logger.info("Progress saved. Run again to resume.")

        return self.scraped_listings

    def save_to_csv(self, filename: str = None):
        """Save scraped data to CSV"""
        if not self.scraped_listings:
            logger.warning("No listings to save")
            return

        if filename is None:
            filename = f"../data/turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        data = [asdict(listing) for listing in self.scraped_listings]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"Saved {len(self.scraped_listings)} listings to {filename}")

    def save_to_excel(self, filename: str = None):
        """Save scraped data to Excel"""
        if not self.scraped_listings:
            logger.warning("No listings to save")
            return

        if filename is None:
            filename = f"../data/turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        data = [asdict(listing) for listing in self.scraped_listings]
        df = pd.DataFrame(data)

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Listings', index=False)

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
            filename = f"../data/turbo_az_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = [asdict(listing) for listing in self.scraped_listings]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(self.scraped_listings)} listings to {filename}")

    def save_to_postgres(self):
        """Save scraped data to PostgreSQL database"""
        if not self.scraped_listings:
            logger.warning("No listings to save to PostgreSQL")
            return

        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            logger.error("DATABASE_URL not found in environment variables")
            logger.error("Skipping PostgreSQL save")
            return

        logger.info("="*60)
        logger.info("SAVING TO POSTGRESQL")
        logger.info("="*60)

        try:
            # Connect to database
            logger.info("Connecting to PostgreSQL...")
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            logger.info("Connected successfully!")

            # Helper functions for data conversion
            def parse_phone_numbers(phone_str):
                """Convert phone string to JSON array"""
                if not phone_str or phone_str == '':
                    return None
                phones = [p.strip() for p in str(phone_str).split('|') if p.strip()]
                return json.dumps(phones) if phones else None

            def parse_integer(val):
                """Safely parse integer values"""
                if not val or val == '':
                    return None
                try:
                    return int(float(val))
                except:
                    return None

            def parse_timestamp(val):
                """Parse timestamp string"""
                if not val or val == '':
                    return None
                try:
                    return datetime.fromisoformat(val.replace('Z', '+00:00'))
                except:
                    return None

            # Prepare SQL
            insert_sql = """
            INSERT INTO scraping.turbo_az (
                listing_id, listing_url, title, price_azn,
                make, model, year, mileage, engine_volume, engine_power, fuel_type,
                transmission, drivetrain, body_type, color, seats_count,
                condition, market, is_new, city, seller_name, seller_phone,
                description, extras, views, updated_date, posted_date,
                is_vip, is_featured, is_salon, has_credit, has_barter, has_vin,
                image_urls, scraped_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (listing_id) DO UPDATE SET
                listing_url = EXCLUDED.listing_url,
                title = EXCLUDED.title,
                price_azn = EXCLUDED.price_azn,
                make = EXCLUDED.make,
                model = EXCLUDED.model,
                year = EXCLUDED.year,
                mileage = EXCLUDED.mileage,
                engine_volume = EXCLUDED.engine_volume,
                engine_power = EXCLUDED.engine_power,
                fuel_type = EXCLUDED.fuel_type,
                transmission = EXCLUDED.transmission,
                drivetrain = EXCLUDED.drivetrain,
                body_type = EXCLUDED.body_type,
                color = EXCLUDED.color,
                seats_count = EXCLUDED.seats_count,
                condition = EXCLUDED.condition,
                market = EXCLUDED.market,
                is_new = EXCLUDED.is_new,
                city = EXCLUDED.city,
                seller_name = EXCLUDED.seller_name,
                seller_phone = EXCLUDED.seller_phone,
                description = EXCLUDED.description,
                extras = EXCLUDED.extras,
                views = EXCLUDED.views,
                updated_date = EXCLUDED.updated_date,
                posted_date = EXCLUDED.posted_date,
                is_vip = EXCLUDED.is_vip,
                is_featured = EXCLUDED.is_featured,
                is_salon = EXCLUDED.is_salon,
                has_credit = EXCLUDED.has_credit,
                has_barter = EXCLUDED.has_barter,
                has_vin = EXCLUDED.has_vin,
                image_urls = EXCLUDED.image_urls,
                scraped_at = EXCLUDED.scraped_at;
            """

            # Prepare batch data
            logger.info(f"Processing {len(self.scraped_listings)} listings...")
            batch_data = []
            errors = 0

            for listing in self.scraped_listings:
                try:
                    data_tuple = (
                        parse_integer(listing.listing_id),
                        listing.listing_url if listing.listing_url else None,
                        listing.title if listing.title else None,
                        listing.price_azn if listing.price_azn else None,

                        listing.make if listing.make else None,
                        listing.model if listing.model else None,
                        parse_integer(listing.year),
                        listing.mileage if listing.mileage else None,
                        listing.engine_volume if listing.engine_volume else None,
                        listing.engine_power if listing.engine_power else None,
                        listing.fuel_type if listing.fuel_type else None,

                        listing.transmission if listing.transmission else None,
                        listing.drivetrain if listing.drivetrain else None,
                        listing.body_type if listing.body_type else None,
                        listing.color if listing.color else None,
                        parse_integer(listing.seats_count),

                        listing.condition if listing.condition else None,
                        listing.market if listing.market else None,
                        listing.is_new if listing.is_new else None,
                        listing.city if listing.city else None,
                        listing.seller_name if listing.seller_name else None,
                        parse_phone_numbers(listing.seller_phone),

                        listing.description if listing.description else None,
                        listing.extras if listing.extras else None,
                        parse_integer(listing.views),
                        listing.updated_date if listing.updated_date else None,
                        listing.posted_date if listing.posted_date else None,

                        listing.is_vip,
                        listing.is_featured,
                        listing.is_salon,
                        listing.has_credit,
                        listing.has_barter,
                        listing.has_vin,

                        listing.image_urls if listing.image_urls else None,
                        parse_timestamp(listing.scraped_at),
                    )
                    batch_data.append(data_tuple)

                except Exception as e:
                    errors += 1
                    logger.error(f"Error processing listing {listing.listing_id}: {e}")

            logger.info(f"Processed {len(batch_data)} listings ({errors} errors)")

            # Batch insert with URL conflict handling
            logger.info("Inserting into PostgreSQL...")
            batch_size = 500
            total_inserted = 0
            total_skipped = 0

            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]

                try:
                    execute_batch(cursor, insert_sql, batch, page_size=100)
                    conn.commit()
                    total_inserted += len(batch)
                    logger.info(f"  Inserted {total_inserted}/{len(batch_data)} listings...")

                except psycopg2.errors.UniqueViolation as e:
                    conn.rollback()

                    if 'unique_listing_url' in str(e):
                        logger.warning(f"⚠️ URL duplicate detected in batch, falling back to individual inserts")

                        # Fallback: Insert one by one to identify and skip duplicates
                        for single_data in batch:
                            try:
                                cursor.execute(insert_sql, single_data)
                                conn.commit()
                                total_inserted += 1
                            except psycopg2.errors.UniqueViolation as single_error:
                                conn.rollback()
                                if 'unique_listing_url' in str(single_error):
                                    total_skipped += 1
                                    logger.warning(f"   Skipped duplicate URL for listing_id: {single_data[0]}")
                                else:
                                    # Different uniqueness error, re-raise
                                    raise
                            except Exception as single_error:
                                conn.rollback()
                                logger.error(f"   Error inserting listing {single_data[0]}: {single_error}")
                                total_skipped += 1

                        logger.info(f"  Batch complete: {total_inserted - (i//batch_size * batch_size)} inserted, {total_skipped} skipped")

                    else:
                        # Different UniqueViolation (not URL), re-raise
                        raise

                except Exception as batch_error:
                    conn.rollback()
                    logger.error(f"Batch insert error: {batch_error}")
                    # Try individual inserts as fallback
                    for single_data in batch:
                        try:
                            cursor.execute(insert_sql, single_data)
                            conn.commit()
                            total_inserted += 1
                        except Exception as e:
                            conn.rollback()
                            total_skipped += 1
                            logger.error(f"   Failed to insert listing {single_data[0]}: {e}")

            logger.info(f"✅ Successfully saved {total_inserted} listings to PostgreSQL!")
            if total_skipped > 0:
                logger.info(f"⚠️ Skipped {total_skipped} duplicate listings")

            # Get stats
            cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az;")
            total_in_db = cursor.fetchone()[0]
            logger.info(f"📊 Total listings in database: {total_in_db:,}")

            cursor.close()
            conn.close()

            logger.info("="*60)

        except psycopg2.Error as e:
            logger.error(f"PostgreSQL error: {e}")
            logger.error("Data was saved to CSV but not to database")
            if 'conn' in locals():
                conn.rollback()
        except Exception as e:
            logger.error(f"Error saving to PostgreSQL: {e}")
            logger.error("Data was saved to CSV but not to database")


async def main():
    """Main execution function"""

    # Load environment variables from .env file
    load_dotenv()

    # Configuration from environment variables with fallback defaults
    START_PAGE = int(os.getenv('START_PAGE', '1'))
    END_PAGE = int(os.getenv('END_PAGE', '1770'))
    BASE_URL = os.getenv('BASE_URL', 'https://turbo.az/autos')
    MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', '3'))
    DELAY = float(os.getenv('DELAY', '2'))
    AUTO_SAVE_INTERVAL = int(os.getenv('AUTO_SAVE_INTERVAL', '50'))

    # BrightData Proxy Configuration from environment
    # Supports both single proxy and multiple proxies (comma-separated)
    proxy_env = os.getenv('PROXY_URL', '').strip()

    if proxy_env:
        # Check if multiple proxies (comma-separated)
        if ',' in proxy_env:
            PROXY_URL = [p.strip() for p in proxy_env.split(',') if p.strip()]
            logger.info(f"Loaded {len(PROXY_URL)} proxies from .env file")
        else:
            PROXY_URL = proxy_env
            logger.info("Loaded single proxy from .env file")
    else:
        PROXY_URL = None
        logger.info("No proxy configured in .env file")

    logger.info("="*60)
    logger.info("Turbo.az Scraper with Crash Recovery")
    logger.info("="*60)
    logger.info(f"Pages: {START_PAGE} to {END_PAGE}")
    logger.info(f"Auto-save every: {AUTO_SAVE_INTERVAL} listings")
    logger.info(f"Press Ctrl+C to stop and save progress")
    logger.info("="*60)

    start_time = time.time()

    try:
        async with TurboAzScraper(
            max_concurrent_requests=MAX_CONCURRENT,
            delay_between_requests=DELAY,
            proxy_url=PROXY_URL
        ) as scraper:
            listings = await scraper.scrape_all_pages(
                start_page=START_PAGE,
                end_page=END_PAGE,
                base_search_url=BASE_URL,
                auto_save_interval=AUTO_SAVE_INTERVAL
            )

            if listings:
                # Save directly to PostgreSQL (no CSV backup)
                scraper.save_to_postgres()

        elapsed_time = time.time() - start_time
        logger.info("="*60)
        logger.info(f"Completed in {elapsed_time:.2f} seconds")
        logger.info(f"Total listings: {len(listings)}")
        if listings:
            logger.info(f"Average time per listing: {elapsed_time/len(listings):.2f}s")
        logger.info("="*60)

    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user. Progress saved!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.info("Progress saved to checkpoint. Run again to resume.")


if __name__ == "__main__":
    asyncio.run(main())
