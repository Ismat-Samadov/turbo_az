"""
Phone Number Utilities
Helper functions to query and work with phone numbers in the database
"""

import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

class PhoneUtils:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))

    def close(self):
        self.conn.close()

    def get_listings_with_phones(self, phone_count=None, limit=100):
        """
        Get listings with phone numbers

        Args:
            phone_count: Filter by number of phones (1, 2, 3, etc.) or None for all
            limit: Maximum number of results
        """
        cursor = self.conn.cursor()

        if phone_count:
            query = """
                SELECT listing_id, listing_url, title, seller_name, seller_phone
                FROM scraping.turbo_az
                WHERE seller_phone IS NOT NULL
                  AND jsonb_array_length(seller_phone) = %s
                ORDER BY listing_id DESC
                LIMIT %s
            """
            cursor.execute(query, (phone_count, limit))
        else:
            query = """
                SELECT listing_id, listing_url, title, seller_name, seller_phone
                FROM scraping.turbo_az
                WHERE seller_phone IS NOT NULL
                ORDER BY listing_id DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'listing_id': row[0],
                'url': row[1],
                'title': row[2],
                'seller_name': row[3],
                'phones': row[4]  # Already a Python list
            })

        cursor.close()
        return results

    def get_phone_by_index(self, listing_id, phone_index=0):
        """
        Get specific phone number by index from a listing

        Args:
            listing_id: Listing ID
            phone_index: Index of phone (0=first, 1=second, etc.)
        """
        cursor = self.conn.cursor()

        # JSONB arrays are 0-indexed in PostgreSQL
        query = """
            SELECT seller_phone->%s as phone
            FROM scraping.turbo_az
            WHERE listing_id = %s
              AND seller_phone IS NOT NULL
        """

        cursor.execute(query, (phone_index, listing_id))
        result = cursor.fetchone()
        cursor.close()

        return result[0] if result else None

    def search_by_phone(self, phone_number):
        """
        Search for listings by phone number

        Args:
            phone_number: Full or partial phone number to search
        """
        cursor = self.conn.cursor()

        # Search in JSONB array
        query = """
            SELECT listing_id, listing_url, title, seller_name, seller_phone
            FROM scraping.turbo_az
            WHERE seller_phone::text ILIKE %s
            ORDER BY listing_id DESC
        """

        cursor.execute(query, (f'%{phone_number}%',))

        results = []
        for row in cursor.fetchall():
            results.append({
                'listing_id': row[0],
                'url': row[1],
                'title': row[2],
                'seller_name': row[3],
                'phones': row[4]
            })

        cursor.close()
        return results

    def get_phone_statistics(self):
        """Get detailed statistics about phone numbers"""
        cursor = self.conn.cursor()

        stats = {}

        # Total listings with phones
        cursor.execute("""
            SELECT COUNT(*)
            FROM scraping.turbo_az
            WHERE seller_phone IS NOT NULL
        """)
        stats['total_with_phones'] = cursor.fetchone()[0]

        # Distribution by phone count
        cursor.execute("""
            SELECT
                jsonb_array_length(seller_phone) as phone_count,
                COUNT(*) as listing_count
            FROM scraping.turbo_az
            WHERE seller_phone IS NOT NULL
            GROUP BY jsonb_array_length(seller_phone)
            ORDER BY phone_count
        """)

        stats['distribution'] = {}
        for count, listings in cursor.fetchall():
            stats['distribution'][count] = listings

        # Most common phone numbers (dealers)
        cursor.execute("""
            SELECT
                phone,
                COUNT(*) as usage_count
            FROM scraping.turbo_az,
                 jsonb_array_elements_text(seller_phone) as phone
            WHERE seller_phone IS NOT NULL
            GROUP BY phone
            HAVING COUNT(*) > 1
            ORDER BY usage_count DESC
            LIMIT 20
        """)

        stats['most_common_phones'] = []
        for phone, count in cursor.fetchall():
            stats['most_common_phones'].append({
                'phone': phone,
                'listings': count
            })

        cursor.close()
        return stats

    def export_phones_csv(self, filename='phone_numbers.csv'):
        """Export all phone numbers to CSV"""
        import csv

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                listing_id,
                title,
                make,
                model,
                year,
                price_azn,
                city,
                seller_name,
                seller_phone
            FROM scraping.turbo_az
            WHERE seller_phone IS NOT NULL
            ORDER BY listing_id DESC
        """)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Listing ID', 'Title', 'Make', 'Model', 'Year',
                'Price', 'City', 'Seller Name',
                'Phone 1', 'Phone 2', 'Phone 3', 'Phone 4', 'Phone 5'
            ])

            # Data
            for row in cursor.fetchall():
                phones = row[8] if row[8] else []

                # Pad phones to 5 columns
                phone_cols = phones + [''] * (5 - len(phones))

                writer.writerow([
                    row[0],  # listing_id
                    row[1],  # title
                    row[2],  # make
                    row[3],  # model
                    row[4],  # year
                    row[5],  # price_azn
                    row[6],  # city
                    row[7],  # seller_name
                    *phone_cols[:5]  # First 5 phones
                ])

        cursor.close()
        print(f"✅ Exported to {filename}")


def demo():
    """Demo usage of phone utilities"""
    utils = PhoneUtils()

    print("=" * 80)
    print("PHONE UTILITIES DEMO")
    print("=" * 80)

    # Get statistics
    print("\n📊 Phone Statistics:")
    stats = utils.get_phone_statistics()
    print(f"Total listings with phones: {stats['total_with_phones']:,}")
    print("\nDistribution:")
    for count, listings in stats['distribution'].items():
        print(f"  {count} phone(s): {listings:,} listings")

    # Most common phones (dealers)
    print("\n🏢 Top 10 Dealer Phone Numbers:")
    for i, item in enumerate(stats['most_common_phones'][:10], 1):
        print(f"  {i}. {item['phone']}: {item['listings']} listings")

    # Get listings with multiple phones
    print("\n📱 Sample: Listings with 3 phones:")
    listings = utils.get_listings_with_phones(phone_count=3, limit=5)
    for listing in listings:
        print(f"\n  Listing {listing['listing_id']}: {listing['title']}")
        for i, phone in enumerate(listing['phones'], 1):
            print(f"    Phone {i}: {phone}")

    # Search by phone number
    print("\n🔍 Search Example: Find all listings with '50 400 19 24'")
    results = utils.search_by_phone('50 400 19 24')
    print(f"Found {len(results)} listings")
    for result in results[:3]:
        print(f"  - {result['title']}: {', '.join(result['phones'])}")

    # Get specific phone by index
    print("\n🎯 Extract Second Phone from Listing 7265016:")
    phone = utils.get_phone_by_index(7265016, phone_index=1)
    print(f"  Second phone: {phone}")

    utils.close()

if __name__ == "__main__":
    demo()
