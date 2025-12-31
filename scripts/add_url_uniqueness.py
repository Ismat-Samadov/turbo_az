#!/usr/bin/env python3
"""
Add URL Uniqueness Constraint to Database
Upgrades the database schema to prevent duplicate listings by URL
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("="*80)
print("DATABASE UPGRADE: Adding URL Uniqueness Constraint")
print("="*80)

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

try:
    # Connect to PostgreSQL
    print("\n📡 Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False  # Use transactions for safety
    cursor = conn.cursor()
    print("✅ Connected successfully!")

    # Step 1: Check for existing duplicates by URL
    print("\n" + "="*80)
    print("STEP 1: Checking for existing duplicates by URL")
    print("="*80)

    cursor.execute("""
        SELECT listing_url, COUNT(*) as count
        FROM scraping.turbo_az
        GROUP BY listing_url
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10;
    """)

    duplicates = cursor.fetchall()

    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} URLs with duplicates:")
        print(f"\n{'URL':<60} {'Count'}")
        print("-" * 70)
        for url, count in duplicates:
            print(f"{url[:57]+'...' if len(url) > 60 else url:<60} {count}")

        print("\n🔧 Cleaning up duplicates (keeping most recent)...")

        # Keep only the most recent entry for each URL
        cursor.execute("""
            WITH duplicates AS (
                SELECT listing_id,
                       ROW_NUMBER() OVER (
                           PARTITION BY listing_url
                           ORDER BY scraped_at DESC, created_at DESC
                       ) as rn
                FROM scraping.turbo_az
            )
            DELETE FROM scraping.turbo_az
            WHERE listing_id IN (
                SELECT listing_id FROM duplicates WHERE rn > 1
            );
        """)

        deleted_count = cursor.rowcount
        print(f"✅ Removed {deleted_count} duplicate entries")
    else:
        print("✅ No duplicate URLs found - database is clean!")

    # Step 2: Add UNIQUE constraint on listing_url
    print("\n" + "="*80)
    print("STEP 2: Adding UNIQUE constraint on listing_url")
    print("="*80)

    try:
        cursor.execute("""
            ALTER TABLE scraping.turbo_az
            ADD CONSTRAINT unique_listing_url UNIQUE (listing_url);
        """)
        print("✅ UNIQUE constraint 'unique_listing_url' added successfully!")
    except psycopg2.errors.DuplicateTable:
        print("ℹ️  UNIQUE constraint already exists - skipping")
        conn.rollback()
        conn.autocommit = False

    # Step 3: Create index on listing_url for faster lookups
    print("\n" + "="*80)
    print("STEP 3: Creating index on listing_url")
    print("="*80)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_turbo_az_listing_url
        ON scraping.turbo_az (listing_url);
    """)
    print("✅ Index 'idx_turbo_az_listing_url' created!")

    # Step 4: Create duplicate monitoring view
    print("\n" + "="*80)
    print("STEP 4: Creating duplicate monitoring view")
    print("="*80)

    cursor.execute("""
        CREATE OR REPLACE VIEW scraping.duplicate_detection AS
        SELECT
            'listing_id' as conflict_type,
            listing_id::TEXT as conflict_value,
            COUNT(*) as occurrences
        FROM scraping.turbo_az
        GROUP BY listing_id
        HAVING COUNT(*) > 1

        UNION ALL

        SELECT
            'listing_url' as conflict_type,
            listing_url as conflict_value,
            COUNT(*) as occurrences
        FROM scraping.turbo_az
        GROUP BY listing_url
        HAVING COUNT(*) > 1;
    """)
    print("✅ View 'scraping.duplicate_detection' created!")

    # Step 5: Verify the upgrade
    print("\n" + "="*80)
    print("STEP 5: Verifying constraints")
    print("="*80)

    # Check constraints
    cursor.execute("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = 'scraping'
        AND table_name = 'turbo_az'
        AND constraint_name LIKE '%unique%'
        ORDER BY constraint_name;
    """)

    constraints = cursor.fetchall()
    print(f"\n📋 Unique Constraints on scraping.turbo_az:")
    for name, ctype in constraints:
        print(f"   • {name} ({ctype})")

    # Check indexes
    cursor.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'scraping'
        AND tablename = 'turbo_az'
        ORDER BY indexname;
    """)

    indexes = cursor.fetchall()
    print(f"\n📋 Indexes on scraping.turbo_az ({len(indexes)} total):")
    for (idx,) in indexes:
        print(f"   • {idx}")

    # Commit all changes
    conn.commit()
    print("\n" + "="*80)
    print("✅ DATABASE UPGRADE COMPLETE!")
    print("="*80)

    print("\n📝 Summary:")
    print(f"   • Removed duplicates: {deleted_count if duplicates else 0}")
    print(f"   • Added UNIQUE constraint: listing_url")
    print(f"   • Created index: idx_turbo_az_listing_url")
    print(f"   • Created view: scraping.duplicate_detection")

    print("\n🔍 Test duplicate detection:")
    print("   SELECT * FROM scraping.duplicate_detection;")

    print("\n💡 Next step: Update scraper to handle URL conflicts")
    print("   (Script already handles this with ON CONFLICT)")

    # Close connection
    cursor.close()
    conn.close()

except psycopg2.errors.UniqueViolation as e:
    print(f"\n❌ Unique constraint violation during cleanup: {e}")
    print("   Some duplicates may still exist. Run the script again.")
    conn.rollback()
    exit(1)

except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    conn.rollback()
    exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    if conn:
        conn.rollback()
    exit(1)
