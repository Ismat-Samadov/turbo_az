"""
Analyze phone numbers in the database
Check how they're currently stored and identify issues
"""

import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

def analyze_phone_numbers():
    """Analyze phone number storage in database"""

    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("=" * 80)
    print("PHONE NUMBER ANALYSIS")
    print("=" * 80)

    # Get total listings
    cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az")
    total = cursor.fetchone()[0]
    print(f"\nTotal listings: {total:,}")

    # Get listings with phone numbers
    cursor.execute("""
        SELECT COUNT(*)
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL
    """)
    with_phones = cursor.fetchone()[0]
    print(f"Listings with phones: {with_phones:,} ({with_phones/total*100:.1f}%)")

    # Get sample phone numbers to see structure
    cursor.execute("""
        SELECT listing_id, seller_phone
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL
        LIMIT 20
    """)

    print("\n" + "=" * 80)
    print("SAMPLE DATA (First 20 listings with phones)")
    print("=" * 80)

    issues = {
        'correct_array': 0,
        'string_with_pipes': 0,
        'single_string': 0,
        'invalid_json': 0,
        'empty': 0
    }

    samples = cursor.fetchall()
    for listing_id, phone_data in samples:
        print(f"\nListing ID: {listing_id}")
        print(f"Type: {type(phone_data)}")
        print(f"Raw value: {phone_data}")

        # Analyze structure
        if phone_data is None:
            issues['empty'] += 1
            print("Status: EMPTY")
        elif isinstance(phone_data, list):
            issues['correct_array'] += 1
            print(f"Status: ✅ CORRECT ARRAY (length: {len(phone_data)})")
            print(f"Phones: {', '.join(phone_data)}")
        elif isinstance(phone_data, str):
            if '|' in phone_data:
                issues['string_with_pipes'] += 1
                print("Status: ⚠️ STRING WITH PIPES (should be array)")
                print(f"Phones: {phone_data}")
            else:
                issues['single_string'] += 1
                print("Status: ⚠️ SINGLE STRING (should be array)")
                print(f"Phone: {phone_data}")
        else:
            issues['invalid_json'] += 1
            print("Status: ❌ INVALID")

    # Analyze all phone numbers in database
    print("\n" + "=" * 80)
    print("FULL DATABASE ANALYSIS")
    print("=" * 80)

    # Check JSONB array type
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE jsonb_array_length(seller_phone) = 1) as single_phone,
            COUNT(*) FILTER (WHERE jsonb_array_length(seller_phone) = 2) as two_phones,
            COUNT(*) FILTER (WHERE jsonb_array_length(seller_phone) = 3) as three_phones,
            COUNT(*) FILTER (WHERE jsonb_array_length(seller_phone) >= 4) as four_plus_phones
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL
          AND jsonb_typeof(seller_phone) = 'array'
    """)

    result = cursor.fetchone()
    if result[0] > 0:
        print(f"\nListings with JSONB arrays: {result[0]:,}")
        print(f"  - 1 phone: {result[1]:,}")
        print(f"  - 2 phones: {result[2]:,}")
        print(f"  - 3 phones: {result[3]:,}")
        print(f"  - 4+ phones: {result[4]:,}")

    # Check for text strings (should be converted)
    cursor.execute("""
        SELECT COUNT(*)
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL
          AND jsonb_typeof(seller_phone) = 'string'
    """)

    string_count = cursor.fetchone()[0]
    if string_count > 0:
        print(f"\n⚠️ WARNING: {string_count:,} listings have phone as STRING (should be array)")

    # Get examples of multi-phone listings
    print("\n" + "=" * 80)
    print("EXAMPLES OF MULTI-PHONE LISTINGS")
    print("=" * 80)

    cursor.execute("""
        SELECT listing_id, listing_url, seller_phone
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL
          AND jsonb_typeof(seller_phone) = 'array'
          AND jsonb_array_length(seller_phone) >= 2
        LIMIT 10
    """)

    for listing_id, url, phones in cursor.fetchall():
        print(f"\nListing {listing_id}:")
        print(f"  URL: {url}")
        print(f"  Phones: {json.dumps(phones, ensure_ascii=False)}")
        print(f"  Count: {len(phones)}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)

    print(f"\n✅ Correct format (JSONB array): {result[0]:,}")
    print(f"⚠️ Needs fixing (string): {string_count:,}")

    if string_count > 0:
        print("\n🔧 ACTION REQUIRED:")
        print("1. Run normalization script to convert strings to arrays")
        print("2. Update scraper to save phones as JSONB arrays")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_phone_numbers()
