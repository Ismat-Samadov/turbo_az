"""
Test phone number extraction on a few listings
"""
import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re
from urllib.parse import quote

load_dotenv()

async def test_phone_extraction():
    """Test phone extraction on recent listings"""

    # Test URLs (recent listings)
    test_urls = [
        "https://turbo.az/autos/7418416",
        "https://turbo.az/autos/7418412",
        "https://turbo.az/autos/7418408",
    ]

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)
    cookie_jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(
        connector=connector,
        cookie_jar=cookie_jar,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'az,en-US;q=0.9,en;q=0.8',
        },
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:

        for url in test_urls:
            print("\n" + "=" * 80)
            print(f"Testing: {url}")
            print("=" * 80)

            # Extract listing ID
            match = re.search(r'/autos/(\d+)', url)
            listing_id = match.group(1) if match else ""
            print(f"Listing ID: {listing_id}")

            # Fetch main page
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"❌ Failed to fetch page: {response.status}")
                    continue

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract CSRF token
                csrf_meta = soup.find('meta', {'name': 'csrf-token'})
                csrf_token = csrf_meta.get('content') if csrf_meta else None
                print(f"CSRF Token: {csrf_token[:20]}..." if csrf_token else "CSRF Token: Not found")

                # Build phone URL
                encoded_url = quote(url, safe='')
                phone_url = f"https://turbo.az/autos/{listing_id}/show_phones?trigger_button=main&source_link={encoded_url}"

                # Try to fetch phones
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': url,
                }

                if csrf_token:
                    headers['X-CSRF-Token'] = csrf_token

                print(f"\n📞 Fetching phones from: {phone_url[:80]}...")

                await asyncio.sleep(1)  # Rate limiting

                async with session.get(phone_url, headers=headers) as phone_response:
                    print(f"Status: {phone_response.status}")
                    print(f"Content-Type: {phone_response.headers.get('Content-Type')}")

                    if phone_response.status == 200:
                        try:
                            data = await phone_response.json()
                            print(f"Response JSON: {data}")

                            phones = data.get('phones', [])
                            if phones:
                                print(f"✅ Found {len(phones)} phone(s):")
                                for phone in phones:
                                    print(f"   {phone.get('primary', phone.get('raw', ''))}")
                            else:
                                print("⚠️  No phones in response")
                        except Exception as e:
                            text = await phone_response.text()
                            print(f"❌ JSON parsing failed: {e}")
                            print(f"Response text: {text[:200]}")
                    else:
                        text = await phone_response.text()
                        print(f"❌ Failed: {phone_response.status}")
                        print(f"Response: {text[:500]}")

if __name__ == "__main__":
    asyncio.run(test_phone_extraction())
