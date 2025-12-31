"""
Data Normalization Script
Cleans and normalizes existing data in the turbo_az table
"""

import psycopg2
from dotenv import load_dotenv
import os
import re

load_dotenv()

def normalize_price(price_str):
    """Convert price string to integer (remove spaces, symbols)"""
    if not price_str:
        return None
    # Remove spaces, ₼ symbol, AZN text, commas
    clean = re.sub(r'[^\d]', '', str(price_str))
    return int(clean) if clean else None

def normalize_mileage(mileage_str):
    """Convert mileage to integer (remove 'km', spaces)"""
    if not mileage_str:
        return None
    # Remove km, spaces, commas
    clean = re.sub(r'[^\d]', '', str(mileage_str))
    return int(clean) if clean else None

def normalize_engine_power(power_str):
    """Extract numeric HP value"""
    if not power_str:
        return None
    # Extract first number
    match = re.search(r'\d+', str(power_str))
    return int(match.group()) if match else None

def normalize_data():
    """Run full normalization on database"""

    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("=" * 80)
    print("DATA NORMALIZATION")
    print("=" * 80)

    # Create new normalized columns
    print("\n📋 Step 1: Adding normalized columns...")

    cursor.execute("""
        ALTER TABLE scraping.turbo_az
        ADD COLUMN IF NOT EXISTS price_clean INTEGER,
        ADD COLUMN IF NOT EXISTS mileage_clean INTEGER,
        ADD COLUMN IF NOT EXISTS engine_power_clean INTEGER;
    """)
    conn.commit()
    print("✅ Normalized columns added")

    # Normalize price
    print("\n💰 Step 2: Normalizing prices...")
    cursor.execute("""
        SELECT listing_id, price_azn
        FROM scraping.turbo_az
        WHERE price_azn IS NOT NULL
    """)

    records = cursor.fetchall()
    updated = 0
    errors = 0

    for listing_id, price_azn in records:
        try:
            clean_price = normalize_price(price_azn)
            if clean_price:
                cursor.execute("""
                    UPDATE scraping.turbo_az
                    SET price_clean = %s
                    WHERE listing_id = %s
                """, (clean_price, listing_id))
                updated += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on listing {listing_id}: {e}")

    conn.commit()
    print(f"✅ Normalized {updated:,} prices ({errors} errors)")

    # Normalize mileage
    print("\n🚗 Step 3: Normalizing mileage...")
    cursor.execute("""
        SELECT listing_id, mileage
        FROM scraping.turbo_az
        WHERE mileage IS NOT NULL
    """)

    records = cursor.fetchall()
    updated = 0
    errors = 0

    for listing_id, mileage in records:
        try:
            clean_mileage = normalize_mileage(mileage)
            if clean_mileage is not None:
                cursor.execute("""
                    UPDATE scraping.turbo_az
                    SET mileage_clean = %s
                    WHERE listing_id = %s
                """, (clean_mileage, listing_id))
                updated += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on listing {listing_id}: {e}")

    conn.commit()
    print(f"✅ Normalized {updated:,} mileage values ({errors} errors)")

    # Normalize engine power
    print("\n⚡ Step 4: Normalizing engine power...")
    cursor.execute("""
        SELECT listing_id, engine_power
        FROM scraping.turbo_az
        WHERE engine_power IS NOT NULL AND engine_power != ''
    """)

    records = cursor.fetchall()
    updated = 0
    errors = 0

    for listing_id, engine_power in records:
        try:
            clean_power = normalize_engine_power(engine_power)
            if clean_power:
                cursor.execute("""
                    UPDATE scraping.turbo_az
                    SET engine_power_clean = %s
                    WHERE listing_id = %s
                """, (clean_power, listing_id))
                updated += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on listing {listing_id}: {e}")

    conn.commit()
    print(f"✅ Normalized {updated:,} engine power values ({errors} errors)")

    # Verification
    print("\n📊 Step 5: Verification...")
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(price_clean) as price_clean_count,
            COUNT(mileage_clean) as mileage_clean_count,
            COUNT(engine_power_clean) as power_clean_count
        FROM scraping.turbo_az
    """)

    result = cursor.fetchone()
    print(f"  Total records: {result[0]:,}")
    print(f"  Clean prices: {result[1]:,}")
    print(f"  Clean mileage: {result[2]:,}")
    print(f"  Clean engine power: {result[3]:,}")

    # Sample comparisons
    print("\n📝 Sample comparisons (original vs cleaned):")
    cursor.execute("""
        SELECT price_azn, price_clean, mileage, mileage_clean
        FROM scraping.turbo_az
        WHERE price_clean IS NOT NULL AND mileage_clean IS NOT NULL
        LIMIT 5
    """)

    for price_orig, price_clean, mile_orig, mile_clean in cursor.fetchall():
        print(f"  Price: '{price_orig}' → {price_clean}")
        print(f"  Mileage: '{mile_orig}' → {mile_clean}")
        print()

    cursor.close()
    conn.close()

    print("=" * 80)
    print("✅ NORMALIZATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update dashboard queries to use *_clean columns")
    print("2. Update scraper to save clean data directly")
    print("3. Consider creating views with clean data")

if __name__ == "__main__":
    normalize_data()
