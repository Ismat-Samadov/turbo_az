#!/usr/bin/env python3
"""
Turbo.az Async Scraper with aiohttp
High-speed concurrent scraping with proper async/await
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import csv
import pandas as pd
import time
import re
import os
import ssl
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsyncTurboAzScraper:
    """Async scraper for turbo.az with aiohttp"""

    BASE_URL = "https://turbo.az"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    def __init__(self, checkpoint_file: str = None):
        """Initialize the async scraper"""
        self.checkpoint_file = checkpoint_file or config.CHECKPOINT_CONFIG['file']
        self.listings_data = []
        self.scraped_ids = set()
        self.semaphore = asyncio.Semaphore(config.SCRAPING_CONFIG['max_workers'])

        # Setup proxy
        self.proxy_url = self._setup_proxy() if config.PROXY_CONFIG['enabled'] else None

        # Setup SSL context
        self.ssl_context = self._setup_ssl()

        # Load checkpoint
        if config.CHECKPOINT_CONFIG['enabled']:
            self._load_checkpoint()

    def _setup_proxy(self) -> str:
        """Setup Bright Data proxy configuration"""
        username = config.PROXY_CONFIG['username']
        if config.PROXY_CONFIG.get('country'):
            username = f"{username}-country-{config.PROXY_CONFIG['country']}"

        proxy_url = (
            f"http://{username}:"
            f"{config.PROXY_CONFIG['password']}@"
            f"{config.PROXY_CONFIG['host']}:"
            f"{config.PROXY_CONFIG['port']}"
        )

        logger.info(f"Proxy configured: Bright Data (port {config.PROXY_CONFIG['port']})")
        return proxy_url

    def _setup_ssl(self) -> ssl.SSLContext:
        """Setup SSL context for proxy"""
        if config.PROXY_CONFIG.get('verify_ssl') and config.PROXY_CONFIG.get('ssl_cert'):
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(config.PROXY_CONFIG['ssl_cert'])
            return ssl_context
        else:
            # Disable SSL verification
            return False

    def _load_checkpoint(self):
        """Load existing data from checkpoint file"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    self.listings_data = json.load(f)

                for listing in self.listings_data:
                    self.scraped_ids.add(listing['id'])

                logger.info(f"Loaded {len(self.listings_data)} listings from checkpoint")
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")

    def _save_checkpoint(self):
        """Save current data to checkpoint file"""
        if not config.CHECKPOINT_CONFIG['enabled']:
            return

        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.listings_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")

    async def fetch(self, session: aiohttp.ClientSession, url: str, retry: int = 0) -> Optional[str]:
        """Fetch URL content with retry logic"""
        try:
            async with session.get(
                url,
                proxy=self.proxy_url,
                ssl=self.ssl_context,
                timeout=aiohttp.ClientTimeout(total=config.SCRAPING_CONFIG['timeout'])
            ) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            if retry < config.SCRAPING_CONFIG['retry_attempts']:
                logger.warning(f"Timeout (attempt {retry + 1}), retrying: {url}")
                await asyncio.sleep(config.SCRAPING_CONFIG['retry_delay'])
                return await self.fetch(session, url, retry + 1)
            logger.error(f"Timeout after {retry + 1} attempts: {url}")
            return None
        except Exception as e:
            if retry < config.SCRAPING_CONFIG['retry_attempts']:
                logger.warning(f"Request failed (attempt {retry + 1}), retrying: {url}")
                await asyncio.sleep(config.SCRAPING_CONFIG['retry_delay'])
                return await self.fetch(session, url, retry + 1)
            logger.error(f"Request failed after {retry + 1} attempts: {url} - {e}")
            return None

    async def fetch_json(self, session: aiohttp.ClientSession, url: str, params: dict = None) -> Optional[dict]:
        """Fetch JSON data"""
        try:
            headers = self.HEADERS.copy()
            headers.update({
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
            })

            async with session.get(
                url,
                params=params,
                headers=headers,
                proxy=self.proxy_url,
                ssl=self.ssl_context,
                timeout=aiohttp.ClientTimeout(total=config.SCRAPING_CONFIG['timeout'])
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.debug(f"JSON fetch failed: {url} - {e}")
            return None

    async def get_listing_urls_from_page(self, session: aiohttp.ClientSession, page_num: int) -> List[str]:
        """Extract all listing URLs from a specific page"""
        url = f"{self.BASE_URL}/autos?page={page_num}"
        logger.info(f"Fetching page {page_num}")

        html = await self.fetch(session, url)
        if not html:
            return []

        try:
            soup = BeautifulSoup(html, 'html.parser')
            listing_urls = []
            products = soup.find_all('div', class_='products-i')

            for product in products:
                link = product.find('a', class_='products-i__link')
                if link and link.get('href'):
                    full_url = urljoin(self.BASE_URL, link['href'])
                    listing_urls.append(full_url)

            logger.info(f"Found {len(listing_urls)} listings on page {page_num}")
            return listing_urls
        except Exception as e:
            logger.error(f"Error parsing page {page_num}: {e}")
            return []

    def extract_text_safe(self, soup, selector: str, class_name: Optional[str] = None) -> str:
        """Safely extract text from HTML element"""
        try:
            if class_name:
                element = soup.find(selector, class_=class_name)
            else:
                element = soup.find(selector)
            return element.get_text(strip=True) if element else ""
        except:
            return ""

    def extract_property_value(self, soup, label_text: str) -> str:
        """Extract value from product properties by label"""
        try:
            properties = soup.find_all('div', class_='product-properties__i')
            for prop in properties:
                label = prop.find('label', class_='product-properties__i-name')
                if label and label_text.lower() in label.get_text(strip=True).lower():
                    value = prop.find('span', class_='product-properties__i-value')
                    return value.get_text(strip=True) if value else ""
        except:
            return ""
        return ""

    async def get_phone_number(self, session: aiohttp.ClientSession, listing_id: str, listing_url: str) -> List[str]:
        """Fetch phone numbers for a listing"""
        phone_endpoint = f"{self.BASE_URL}/autos/{listing_id}/show_phones"
        params = {
            'trigger_button': 'main',
            'source_link': listing_url
        }

        data = await self.fetch_json(session, phone_endpoint, params)
        if not data:
            return []

        phones = []
        if 'phones' in data:
            for phone_obj in data['phones']:
                if 'primary' in phone_obj:
                    phones.append(phone_obj['primary'])
                elif 'raw' in phone_obj:
                    phones.append(phone_obj['raw'])

        return phones

    async def scrape_listing_details(self, session: aiohttp.ClientSession, listing_url: str) -> Optional[Dict]:
        """Scrape detailed information from a single listing"""

        # Extract ID and check if already scraped
        listing_id = listing_url.split('/')[-1].split('-')[0]

        if listing_id in self.scraped_ids:
            logger.debug(f"Skipping already scraped listing: {listing_id}")
            return None

        async with self.semaphore:  # Limit concurrency
            html = await self.fetch(session, listing_url)
            if not html:
                return None

            try:
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                title_elem = soup.find('h1', class_='product-title')
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Extract price
                price_elem = soup.find('div', class_='product-price__i--bold')
                price = price_elem.get_text(strip=True) if price_elem else ""

                # Extract properties
                city = self.extract_property_value(soup, 'Şəhər')
                brand = self.extract_property_value(soup, 'Marka')
                model = self.extract_property_value(soup, 'Model')
                year = self.extract_property_value(soup, 'Buraxılış ili')
                body_type = self.extract_property_value(soup, 'Ban növü')
                color = self.extract_property_value(soup, 'Rəng')
                engine = self.extract_property_value(soup, 'Mühərrik')
                mileage = self.extract_property_value(soup, 'Yürüş')
                transmission = self.extract_property_value(soup, 'Sürətlər qutusu')
                gear = self.extract_property_value(soup, 'Ötürücü')
                new = self.extract_property_value(soup, 'Yeni')
                seats = self.extract_property_value(soup, 'Yerlərin sayı')
                condition = self.extract_property_value(soup, 'Vəziyyəti')

                # Extract description
                desc_elem = soup.find('div', class_='product-description__content')
                description = desc_elem.get_text(strip=True) if desc_elem else ""

                # Extract extras
                extras = []
                extras_list = soup.find('ul', class_='product-extras')
                if extras_list:
                    for item in extras_list.find_all('li', class_='product-extras__i'):
                        extras.append(item.get_text(strip=True))

                # Extract owner info
                owner_name = self.extract_text_safe(soup, 'div', 'product-owner__info-name')
                owner_region = self.extract_text_safe(soup, 'div', 'product-owner__info-region')

                # Extract statistics
                stats_items = soup.find_all('li', class_='product-statistics__i')
                updated_date = ""
                view_count = ""
                for stat in stats_items:
                    text = stat.get_text(strip=True)
                    if 'Yeniləndi' in text:
                        updated_date = text.replace('Yeniləndi:', '').strip()
                    elif 'Baxışların sayı' in text:
                        view_count = text.replace('Baxışların sayı:', '').strip()

                # Extract images
                images = []
                photo_slider = soup.find('div', class_='product-photos__slider-nav')
                if photo_slider:
                    for img_div in photo_slider.find_all('div', class_='product-photos__slider-nav-i_picture'):
                        style = img_div.get('style', '')
                        match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                        if match:
                            images.append(match.group(1))

                # Get phone numbers
                phones = await self.get_phone_number(session, listing_id, listing_url)

                # Extract labels
                labels = []
                label_container = soup.find('div', class_='product-labels')
                if label_container:
                    label_items = label_container.find_all('div', class_='product-labels__i')
                    for label_item in label_items:
                        labels.append(label_item.get_text(strip=True))

                # Compile data
                listing_data = {
                    'id': listing_id,
                    'url': listing_url,
                    'title': title,
                    'price': price,
                    'city': city,
                    'brand': brand,
                    'model': model,
                    'year': year,
                    'body_type': body_type,
                    'color': color,
                    'engine': engine,
                    'mileage': mileage,
                    'transmission': transmission,
                    'gear': gear,
                    'is_new': new,
                    'seats': seats,
                    'condition': condition,
                    'description': description,
                    'extras': ', '.join(extras),
                    'owner_name': owner_name,
                    'owner_region': owner_region,
                    'updated_date': updated_date,
                    'view_count': view_count,
                    'phones': phones,
                    'images': ', '.join(images),
                    'labels': ', '.join(labels)
                }

                logger.info(f"✓ Scraped: {listing_id} - {brand} {model}")

                # Add delay
                if config.SCRAPING_CONFIG['listing_delay'] > 0:
                    await asyncio.sleep(config.SCRAPING_CONFIG['listing_delay'])

                return listing_data

            except Exception as e:
                logger.error(f"Error scraping {listing_url}: {e}")
                return None

    async def scrape_page(self, session: aiohttp.ClientSession, page_num: int):
        """Scrape a single page"""
        listing_urls = await self.get_listing_urls_from_page(session, page_num)

        if not listing_urls:
            return

        # Create tasks for all listings
        tasks = [self.scrape_listing_details(session, url) for url in listing_urls]

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, dict) and result:
                self.listings_data.append(result)
                self.scraped_ids.add(result['id'])

        # Save checkpoint
        if config.CHECKPOINT_CONFIG['enabled'] and len(self.listings_data) % config.CHECKPOINT_CONFIG['save_frequency'] == 0:
            self._save_checkpoint()

    async def scrape_pages(self, start_page: int, end_page: int):
        """Scrape multiple pages"""
        logger.info(f"Starting async scrape: pages {start_page}-{end_page}")
        start_time = time.time()

        # Create aiohttp session with custom connector
        connector = aiohttp.TCPConnector(
            limit=config.SCRAPING_CONFIG['max_workers'] * 2,
            limit_per_host=config.SCRAPING_CONFIG['max_workers']
        )

        async with aiohttp.ClientSession(headers=self.HEADERS, connector=connector) as session:
            for page_num in range(start_page, end_page + 1):
                logger.info(f"Processing page {page_num}/{end_page}")
                await self.scrape_page(session, page_num)

                # Save checkpoint after each page
                self._save_checkpoint()

                # Add delay between pages
                if config.SCRAPING_CONFIG['page_delay'] > 0:
                    await asyncio.sleep(config.SCRAPING_CONFIG['page_delay'])

        elapsed = time.time() - start_time
        logger.info(f"Completed {end_page - start_page + 1} pages in {elapsed:.1f}s")
        logger.info(f"Total listings: {len(self.listings_data)}")
        logger.info(f"Speed: {len(self.listings_data) / elapsed:.2f} listings/sec")

    def _expand_listings_by_phone(self) -> List[Dict]:
        """Expand listings so each phone number gets its own row"""
        expanded_data = []

        for listing in self.listings_data:
            phones = listing.get('phones', [])

            if not phones:
                listing_copy = listing.copy()
                listing_copy['phone'] = ''
                del listing_copy['phones']
                expanded_data.append(listing_copy)
            else:
                for phone in phones:
                    listing_copy = listing.copy()
                    listing_copy['phone'] = phone
                    del listing_copy['phones']
                    expanded_data.append(listing_copy)

        return expanded_data

    def export_to_json(self, filename: str = 'turbo_listings.json'):
        """Export data to JSON file"""
        try:
            expanded_data = self._expand_listings_by_phone()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(expanded_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ Exported to {filename} ({len(expanded_data)} rows)")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

    def export_to_csv(self, filename: str = 'turbo_listings.csv'):
        """Export data to CSV file"""
        try:
            expanded_data = self._expand_listings_by_phone()
            if not expanded_data:
                logger.warning("No data to export")
                return

            keys = expanded_data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(expanded_data)

            logger.info(f"✓ Exported to {filename} ({len(expanded_data)} rows)")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")

    def export_to_xlsx(self, filename: str = 'turbo_listings.xlsx'):
        """Export data to Excel file"""
        try:
            expanded_data = self._expand_listings_by_phone()
            if not expanded_data:
                logger.warning("No data to export")
                return

            df = pd.DataFrame(expanded_data)
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"✓ Exported to {filename} ({len(expanded_data)} rows)")
        except Exception as e:
            logger.error(f"Error exporting to XLSX: {e}")

    def export_all(self, base_filename: str = 'turbo_listings'):
        """Export data to all formats"""
        self.export_to_json(f"{base_filename}.json")
        self.export_to_csv(f"{base_filename}.csv")
        self.export_to_xlsx(f"{base_filename}.xlsx")

    def clear_checkpoint(self):
        """Clear the checkpoint file"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                logger.info(f"Checkpoint cleared: {self.checkpoint_file}")
        except Exception as e:
            logger.error(f"Error clearing checkpoint: {e}")


async def main():
    """Main async function"""
    try:
        scraper = AsyncTurboAzScraper()

        # Configure pages
        start_page = 1
        end_page = 5

        logger.info("=" * 60)
        logger.info("TURBO.AZ ASYNC SCRAPER")
        logger.info("=" * 60)
        logger.info(f"Pages: {start_page}-{end_page}")
        logger.info(f"Workers: {config.SCRAPING_CONFIG['max_workers']}")
        logger.info(f"Proxy: {'Enabled' if config.PROXY_CONFIG['enabled'] else 'Disabled'}")
        logger.info("=" * 60)

        await scraper.scrape_pages(start_page, end_page)

        # Export
        logger.info("\nExporting data...")
        scraper.export_all('turbo_listings_async')
        scraper.clear_checkpoint()

        logger.info("\n✓ SCRAPING COMPLETED!")

    except KeyboardInterrupt:
        logger.warning("\n⚠ Interrupted by user. Progress saved in checkpoint.")
    except Exception as e:
        logger.error(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        logger.info("Progress saved in checkpoint.")


if __name__ == "__main__":
    asyncio.run(main())
