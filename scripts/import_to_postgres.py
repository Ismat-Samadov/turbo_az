"""
Import Turbo.az CSV data to PostgreSQL
Handles phone numbers as JSON arrays
"""
import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
DATA_FILE = "../data/turbo_az_listings_combined_clean_20251231_090519.csv"

print("="*80)
print("IMPORT TURBO.AZ DATA TO POSTGRESQL")
print("="*80)

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

if not os.path.exists(DATA_FILE):
    print(f"\n❌ ERROR: Data file not found: {DATA_FILE}")
    exit(1)

# Helper functions
def parse_phone_numbers(phone_str):
    """Convert phone string to JSON array"""
    if pd.isna(phone_str) or phone_str == '':
        return None

    # Split by pipe and clean
    phones = [p.strip() for p in str(phone_str).split('|') if p.strip()]
    return json.dumps(phones) if phones else None

def parse_boolean(val):
    """Convert various boolean representations to Python bool"""
    if pd.isna(val) or val == '':
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ('true', '1', 'yes', 't')
    return bool(val)

def parse_integer(val):
    """Safely parse integer values"""
    if pd.isna(val) or val == '':
        return None
    try:
        return int(float(val))
    except:
        return None

def parse_timestamp(val):
    """Parse timestamp string"""
    if pd.isna(val) or val == '':
        return None
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00'))
    except:
        return None

try:
    # Load CSV
    print(f"\n📄 Loading CSV file: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig', low_memory=False)
    print(f"✅ Loaded {len(df):,} rows")

    # Connect to database
    print("\n📡 Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Connected successfully!")

    # Prepare data for insertion
    print("\n🔄 Processing data...")

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

    batch_data = []
    errors = 0

    for idx, row in df.iterrows():
        try:
            data_tuple = (
                parse_integer(row['listing_id']),
                str(row['listing_url']) if pd.notna(row['listing_url']) else None,
                str(row['title']) if pd.notna(row['title']) else None,
                str(row['price_azn']) if pd.notna(row['price_azn']) else None,

                str(row['make']) if pd.notna(row['make']) else None,
                str(row['model']) if pd.notna(row['model']) else None,
                parse_integer(row['year']),
                str(row['mileage']) if pd.notna(row['mileage']) else None,
                str(row['engine_volume']) if pd.notna(row['engine_volume']) else None,
                str(row['engine_power']) if pd.notna(row['engine_power']) else None,
                str(row['fuel_type']) if pd.notna(row['fuel_type']) else None,

                str(row['transmission']) if pd.notna(row['transmission']) else None,
                str(row['drivetrain']) if pd.notna(row['drivetrain']) else None,
                str(row['body_type']) if pd.notna(row['body_type']) else None,
                str(row['color']) if pd.notna(row['color']) else None,
                parse_integer(row['seats_count']),

                str(row['condition']) if pd.notna(row['condition']) else None,
                str(row['market']) if pd.notna(row['market']) else None,
                str(row['is_new']) if pd.notna(row['is_new']) else None,
                str(row['city']) if pd.notna(row['city']) else None,
                str(row['seller_name']) if pd.notna(row['seller_name']) else None,
                parse_phone_numbers(row['seller_phone']),

                str(row['description']) if pd.notna(row['description']) else None,
                str(row['extras']) if pd.notna(row['extras']) else None,
                parse_integer(row['views']),
                str(row['updated_date']) if pd.notna(row['updated_date']) else None,
                str(row['posted_date']) if pd.notna(row['posted_date']) else None,

                parse_boolean(row['is_vip']),
                parse_boolean(row['is_featured']),
                parse_boolean(row['is_salon']),
                parse_boolean(row['has_credit']),
                parse_boolean(row['has_barter']),
                parse_boolean(row['has_vin']),

                str(row['image_urls']) if pd.notna(row['image_urls']) else None,
                parse_timestamp(row['scraped_at']),
            )
            batch_data.append(data_tuple)

            # Progress indicator
            if (idx + 1) % 1000 == 0:
                print(f"   Processed {idx + 1:,}/{len(df):,} rows...")

        except Exception as e:
            errors += 1
            print(f"   ⚠️  Error processing row {idx}: {e}")

    print(f"✅ Processed {len(batch_data):,} rows (Errors: {errors})")

    # Batch insert
    print("\n💾 Inserting data into PostgreSQL...")
    print("   This may take a while...")

    batch_size = 500
    total_batches = (len(batch_data) + batch_size - 1) // batch_size

    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i + batch_size]
        execute_batch(cursor, insert_sql, batch, page_size=100)
        conn.commit()

        batch_num = (i // batch_size) + 1
        print(f"   Batch {batch_num}/{total_batches} inserted ({len(batch)} rows)")

    print(f"✅ All data inserted successfully!")

    # Get statistics
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)

    cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az;")
    total_rows = cursor.fetchone()[0]
    print(f"\n📊 Total rows in table: {total_rows:,}")

    cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az WHERE seller_phone IS NOT NULL;")
    with_phones = cursor.fetchone()[0]
    print(f"📞 Rows with phone numbers: {with_phones:,} ({with_phones/total_rows*100:.1f}%)")

    cursor.execute("SELECT make, COUNT(*) as count FROM scraping.turbo_az GROUP BY make ORDER BY count DESC LIMIT 5;")
    top_makes = cursor.fetchall()
    print(f"\n🚗 Top 5 Makes:")
    for make, count in top_makes:
        print(f"   {make:20} - {count:,} listings")

    cursor.execute("SELECT city, COUNT(*) as count FROM scraping.turbo_az GROUP BY city ORDER BY count DESC LIMIT 5;")
    top_cities = cursor.fetchall()
    print(f"\n🏙️  Top 5 Cities:")
    for city, count in top_cities:
        print(f"   {city:20} - {count:,} listings")

    # Example queries
    print("\n" + "="*80)
    print("EXAMPLE QUERIES")
    print("="*80)

    print("\n-- Get listings with multiple phone numbers:")
    print("SELECT listing_id, title, seller_phone")
    print("FROM scraping.turbo_az")
    print("WHERE jsonb_array_length(seller_phone) > 1")
    print("LIMIT 5;")

    cursor.execute("""
        SELECT listing_id, title, seller_phone
        FROM scraping.turbo_az
        WHERE seller_phone IS NOT NULL AND jsonb_array_length(seller_phone) > 1
        LIMIT 5;
    """)
    multi_phones = cursor.fetchall()

    if multi_phones:
        print(f"\n📱 Found {len(multi_phones)} examples with multiple phones:")
        for listing_id, title, phones in multi_phones:
            print(f"   ID {listing_id}: {phones}")

    print("\n-- Extract phone numbers as array:")
    print("SELECT listing_id, seller_phone->0 as first_phone, seller_phone->1 as second_phone")
    print("FROM scraping.turbo_az")
    print("WHERE seller_phone IS NOT NULL;")

    # Close connection
    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ IMPORT COMPLETE!")
    print("="*80)
    print(f"\n📝 Summary:")
    print(f"   • Total rows imported: {total_rows:,}")
    print(f"   • Rows with phones: {with_phones:,}")
    print(f"   • Processing errors: {errors}")
    print("\n💡 Phone numbers are stored as JSON arrays in seller_phone column")
    print("   Use JSONB operators for querying: ->, ->>, @>, etc.")
    print("\n" + "="*80)

except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    if 'conn' in locals():
        conn.rollback()
    exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
