"""
Data Quality Analysis Script
Analyzes data in turbo_az table to identify issues and normalization needs
"""

import psycopg2
import json
from dotenv import load_dotenv
import os
import re
from collections import Counter

load_dotenv()

def analyze_data_quality():
    """Comprehensive data quality analysis"""

    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("=" * 80)
    print("DATA QUALITY ANALYSIS - TURBO.AZ DATABASE")
    print("=" * 80)

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total Listings: {total:,}")

    # Analyze each column
    columns = [
        'listing_id', 'listing_url', 'title', 'price_azn', 'make', 'model',
        'year', 'mileage', 'engine_volume', 'engine_power', 'fuel_type',
        'transmission', 'drivetrain', 'body_type', 'color', 'seats_count',
        'condition', 'market', 'is_new', 'city', 'seller_name', 'seller_phone',
        'description', 'extras', 'views', 'updated_date', 'posted_date'
    ]

    print("\n" + "=" * 80)
    print("NULL VALUE ANALYSIS")
    print("=" * 80)

    null_stats = []
    for col in columns:
        cursor.execute(f"""
            SELECT
                COUNT(*) as total,
                COUNT({col}) as non_null,
                COUNT(*) - COUNT({col}) as null_count,
                ROUND(100.0 * (COUNT(*) - COUNT({col})) / COUNT(*), 2) as null_percent
            FROM scraping.turbo_az
        """)
        result = cursor.fetchone()
        null_stats.append({
            'column': col,
            'total': result[0],
            'non_null': result[1],
            'null_count': result[2],
            'null_percent': result[3]
        })

    # Sort by null percentage
    null_stats.sort(key=lambda x: x['null_percent'], reverse=True)

    print(f"\n{'Column':<20} {'Non-Null':<12} {'Null':<12} {'Null %':<10}")
    print("-" * 80)
    for stat in null_stats:
        print(f"{stat['column']:<20} {stat['non_null']:<12,} {stat['null_count']:<12,} {stat['null_percent']:<10.2f}%")

    # PRICE ANALYSIS
    print("\n" + "=" * 80)
    print("PRICE FORMAT ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT price_azn, COUNT(*) as count
        FROM scraping.turbo_az
        WHERE price_azn IS NOT NULL
        GROUP BY price_azn
        ORDER BY count DESC
        LIMIT 20
    """)

    print("\nTop 20 Price Formats:")
    price_formats = {}
    for price, count in cursor.fetchall():
        # Analyze format
        has_space = ' ' in price
        has_azn = 'AZN' in price or 'azn' in price
        has_digits = bool(re.search(r'\d', price))
        has_letters = bool(re.search(r'[a-zA-Z]', price))

        format_type = "Unknown"
        if not has_digits:
            format_type = "No digits"
        elif has_azn and has_space:
            format_type = "Standard (with AZN and spaces)"
        elif has_azn:
            format_type = "Has AZN (no spaces)"
        elif has_space:
            format_type = "Has spaces (no AZN)"
        else:
            format_type = "Digits only"

        price_formats[format_type] = price_formats.get(format_type, 0) + count
        print(f"  '{price}': {count:,} times - [{format_type}]")

    print("\nPrice Format Summary:")
    for fmt, count in sorted(price_formats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {fmt}: {count:,}")

    # YEAR ANALYSIS
    print("\n" + "=" * 80)
    print("YEAR FORMAT ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT
            year,
            COUNT(*) as count,
            CASE
                WHEN year IS NULL THEN 'NULL'
                WHEN CAST(year AS TEXT) ~ '^[0-9]{4}$' THEN 'Valid (4 digits)'
                ELSE 'Invalid format'
            END as format_type
        FROM scraping.turbo_az
        GROUP BY year, format_type
        ORDER BY count DESC
        LIMIT 15
    """)

    year_issues = []
    for year, count, fmt in cursor.fetchall():
        if fmt != 'Valid (4 digits)':
            year_issues.append((year, count, fmt))
        print(f"  {year}: {count:,} - [{fmt}]")

    if year_issues:
        print(f"\n⚠️  Found {len(year_issues)} year format issues")

    # MILEAGE ANALYSIS
    print("\n" + "=" * 80)
    print("MILEAGE FORMAT ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT mileage, COUNT(*) as count
        FROM scraping.turbo_az
        WHERE mileage IS NOT NULL
        GROUP BY mileage
        ORDER BY count DESC
        LIMIT 15
    """)

    mileage_formats = {}
    for mileage, count in cursor.fetchall():
        has_km = 'km' in str(mileage).lower()
        has_space = ' ' in str(mileage)
        has_comma = ',' in str(mileage)

        if has_km and has_space:
            fmt = "Standard (with km and spaces)"
        elif has_km:
            fmt = "Has km (no spaces)"
        elif has_comma:
            fmt = "Has comma separator"
        elif str(mileage).isdigit():
            fmt = "Digits only"
        else:
            fmt = "Other format"

        mileage_formats[fmt] = mileage_formats.get(fmt, 0) + count
        print(f"  '{mileage}': {count:,} - [{fmt}]")

    print("\nMileage Format Summary:")
    for fmt, count in sorted(mileage_formats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {fmt}: {count:,}")

    # ENGINE VOLUME/POWER ANALYSIS
    print("\n" + "=" * 80)
    print("ENGINE FORMAT ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT engine_volume, COUNT(*) as count
        FROM scraping.turbo_az
        WHERE engine_volume IS NOT NULL
        GROUP BY engine_volume
        ORDER BY count DESC
        LIMIT 10
    """)

    print("\nTop 10 Engine Volume Formats:")
    for vol, count in cursor.fetchall():
        print(f"  '{vol}': {count:,}")

    # CITY ANALYSIS
    print("\n" + "=" * 80)
    print("CITY DATA ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT city, COUNT(*) as count
        FROM scraping.turbo_az
        WHERE city IS NOT NULL
        GROUP BY city
        ORDER BY count DESC
        LIMIT 15
    """)

    print("\nTop 15 Cities:")
    for city, count in cursor.fetchall():
        print(f"  {city}: {count:,}")

    # PHONE NUMBER ANALYSIS
    print("\n" + "=" * 80)
    print("PHONE NUMBER ANALYSIS")
    print("=" * 80)

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(seller_phone) as with_phone,
            COUNT(*) - COUNT(seller_phone) as without_phone
        FROM scraping.turbo_az
    """)

    total, with_phone, without = cursor.fetchone()
    print(f"\nTotal listings: {total:,}")
    print(f"With phone: {with_phone:,} ({100*with_phone/total:.1f}%)")
    print(f"Without phone: {without:,} ({100*without/total:.1f}%)")

    # Sample problematic records
    print("\n" + "=" * 80)
    print("SAMPLE PROBLEMATIC RECORDS")
    print("=" * 80)

    cursor.execute("""
        SELECT listing_id, title, price_azn, year, mileage, city
        FROM scraping.turbo_az
        WHERE price_azn IS NULL
           OR year IS NULL
           OR city IS NULL
        LIMIT 5
    """)

    print("\nSample records with NULL critical fields:")
    for row in cursor.fetchall():
        print(f"\n  ID: {row[0]}")
        print(f"  Title: {row[1]}")
        print(f"  Price: {row[2]}")
        print(f"  Year: {row[3]}")
        print(f"  Mileage: {row[4]}")
        print(f"  City: {row[5]}")

    # RECOMMENDATIONS
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    print("\n🔧 Data Normalization Needed:")
    print("  1. PRICE: Remove 'AZN' text and spaces, convert to integer")
    print("  2. YEAR: Ensure 4-digit format, convert to integer")
    print("  3. MILEAGE: Remove 'km' text and spaces, convert to integer")
    print("  4. ENGINE_VOLUME: Standardize format (e.g., '2.0 L')")
    print("  5. ENGINE_POWER: Extract numeric value")

    print("\n🐛 Scraper Issues to Fix:")
    print("  1. High NULL rate for seller_phone (90%+) - check AJAX endpoint")
    print("  2. Missing critical fields (price, year, city) - improve parsing")
    print("  3. Inconsistent text formats - apply cleaning during scraping")

    print("\n📋 Next Steps:")
    print("  1. Run normalization script to clean existing data")
    print("  2. Update scraper to save clean data from start")
    print("  3. Add data validation before database insert")
    print("  4. Monitor scraping success rates")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_data_quality()
