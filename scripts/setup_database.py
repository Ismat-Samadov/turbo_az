"""
PostgreSQL Database Setup for Turbo.az Scraper
Creates schema and table structure
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("="*80)
print("POSTGRESQL DATABASE SETUP")
print("="*80)

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

try:
    # Connect to PostgreSQL
    print("\n📡 Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    print("✅ Connected successfully!")

    # Get database info
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    print(f"\n📊 Database: {db_version.split(',')[0]}")

    # Create schema
    print("\n" + "="*80)
    print("CREATING SCHEMA")
    print("="*80)

    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS scraping;
    """)
    print("✅ Schema 'scraping' created (or already exists)")

    # Create turbo_az table
    print("\n" + "="*80)
    print("CREATING TABLE: scraping.turbo_az")
    print("="*80)

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS scraping.turbo_az (
        -- Primary Key
        listing_id BIGINT PRIMARY KEY,

        -- Basic Information
        listing_url TEXT NOT NULL,
        title TEXT NOT NULL,
        price_azn TEXT,

        -- Car Details
        make VARCHAR(100),
        model VARCHAR(100),
        year INTEGER,
        mileage TEXT,
        engine_volume VARCHAR(50),
        engine_power VARCHAR(50),
        fuel_type VARCHAR(50),

        -- Technical Specifications
        transmission VARCHAR(50),
        drivetrain VARCHAR(50),
        body_type VARCHAR(50),
        color VARCHAR(50),
        seats_count INTEGER,
        condition VARCHAR(50),
        market VARCHAR(100),
        is_new VARCHAR(20),

        -- Location & Seller
        city VARCHAR(100),
        seller_name VARCHAR(200),
        seller_phone JSONB,  -- Array of phone numbers

        -- Additional Information
        description TEXT,
        extras TEXT,  -- Pipe-separated list
        views INTEGER,
        updated_date TEXT,
        posted_date TEXT,

        -- Badges/Flags
        is_vip BOOLEAN DEFAULT FALSE,
        is_featured BOOLEAN DEFAULT FALSE,
        is_salon BOOLEAN DEFAULT FALSE,
        has_credit BOOLEAN DEFAULT FALSE,
        has_barter BOOLEAN DEFAULT FALSE,
        has_vin BOOLEAN DEFAULT FALSE,

        -- Media
        image_urls TEXT,  -- Pipe-separated URLs

        -- Metadata
        scraped_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    cursor.execute(create_table_sql)
    print("✅ Table 'scraping.turbo_az' created (or already exists)")

    # Create indexes
    print("\n" + "="*80)
    print("CREATING INDEXES")
    print("="*80)

    indexes = [
        ("idx_turbo_az_make", "make"),
        ("idx_turbo_az_model", "model"),
        ("idx_turbo_az_year", "year"),
        ("idx_turbo_az_city", "city"),
        ("idx_turbo_az_scraped_at", "scraped_at"),
        ("idx_turbo_az_is_vip", "is_vip"),
        ("idx_turbo_az_seller_phone", "seller_phone USING GIN"),
    ]

    for index_name, column in indexes:
        try:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON scraping.turbo_az ({column});
            """)
            print(f"✅ Index '{index_name}' created")
        except Exception as e:
            print(f"⚠️  Index '{index_name}': {e}")

    # Create updated_at trigger
    print("\n" + "="*80)
    print("CREATING TRIGGERS")
    print("="*80)

    cursor.execute("""
        CREATE OR REPLACE FUNCTION scraping.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    print("✅ Function 'update_updated_at_column' created")

    cursor.execute("""
        DROP TRIGGER IF EXISTS update_turbo_az_updated_at ON scraping.turbo_az;
        CREATE TRIGGER update_turbo_az_updated_at
        BEFORE UPDATE ON scraping.turbo_az
        FOR EACH ROW
        EXECUTE FUNCTION scraping.update_updated_at_column();
    """)
    print("✅ Trigger 'update_turbo_az_updated_at' created")

    # Get table info
    print("\n" + "="*80)
    print("TABLE INFORMATION")
    print("="*80)

    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'scraping' AND table_name = 'turbo_az'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()
    print(f"\n📋 Table: scraping.turbo_az")
    print(f"   Total columns: {len(columns)}")
    print("\n" + "-"*80)
    print(f"{'Column Name':<25} {'Data Type':<20} {'Max Length':<12} {'Nullable'}")
    print("-"*80)

    for col in columns:
        col_name, data_type, max_length, nullable = col
        max_len_str = str(max_length) if max_length else "-"
        print(f"{col_name:<25} {data_type:<20} {max_len_str:<12} {nullable}")

    # Check current row count
    cursor.execute("SELECT COUNT(*) FROM scraping.turbo_az;")
    row_count = cursor.fetchone()[0]

    print("\n" + "="*80)
    print("CURRENT DATA")
    print("="*80)
    print(f"\n📊 Current rows in scraping.turbo_az: {row_count:,}")

    # Close connection
    cursor.close()
    conn.close()

    print("\n" + "="*80)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*80)
    print("\n📝 Summary:")
    print(f"   • Schema: scraping")
    print(f"   • Table: turbo_az")
    print(f"   • Columns: {len(columns)}")
    print(f"   • Indexes: {len(indexes)}")
    print(f"   • Current rows: {row_count:,}")
    print("\n💡 Phone numbers are stored as JSONB arrays for easy querying")
    print("   Example query: SELECT * FROM scraping.turbo_az WHERE seller_phone IS NOT NULL;")
    print("\n" + "="*80)

except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
