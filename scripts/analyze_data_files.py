"""
Analyze all data files in /data directory for compatibility
"""
import pandas as pd
import json
import os
from collections import Counter

print("="*80)
print("DATA FILES COMPATIBILITY ANALYSIS")
print("="*80)

data_dir = "../data"

# Find all CSV files
csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
xlsx_files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]

print(f"\n📁 Found {len(csv_files)} CSV files, {len(json_files)} JSON files, {len(xlsx_files)} XLSX files\n")

# Analyze CSV files
print("="*80)
print("CSV FILES ANALYSIS")
print("="*80)

csv_data = {}
all_columns = []

for csv_file in sorted(csv_files):
    filepath = os.path.join(data_dir, csv_file)
    print(f"\n📄 {csv_file}")
    print("-" * 80)

    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig', low_memory=False)
        csv_data[csv_file] = df

        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Size: {os.path.getsize(filepath) / (1024*1024):.2f} MB")
        print(f"  Memory: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")

        # Check for listing_id column
        if 'listing_id' in df.columns:
            unique_ids = df['listing_id'].nunique()
            total_ids = len(df['listing_id'])
            duplicates_within = total_ids - unique_ids
            print(f"  Unique IDs: {unique_ids:,}")
            if duplicates_within > 0:
                print(f"  ⚠️  Duplicates within file: {duplicates_within}")

        all_columns.append((csv_file, list(df.columns)))

    except Exception as e:
        print(f"  ❌ Error reading file: {e}")

# Check column consistency
print("\n" + "="*80)
print("COLUMN COMPATIBILITY CHECK")
print("="*80)

if len(all_columns) > 0:
    first_file, first_cols = all_columns[0]
    all_compatible = True

    print(f"\n📋 Reference columns from: {first_file}")
    print(f"   Total columns: {len(first_cols)}")

    for filename, cols in all_columns[1:]:
        if cols == first_cols:
            print(f"   ✅ {filename} - IDENTICAL columns")
        else:
            print(f"   ⚠️  {filename} - DIFFERENT columns")
            all_compatible = False

            # Show differences
            missing = set(first_cols) - set(cols)
            extra = set(cols) - set(first_cols)
            if missing:
                print(f"      Missing: {missing}")
            if extra:
                print(f"      Extra: {extra}")

    if all_compatible:
        print("\n✅ All CSV files have IDENTICAL column structure - Safe to combine!")
    else:
        print("\n⚠️  CSV files have DIFFERENT structures - Need column alignment")

# Check for duplicates across files
print("\n" + "="*80)
print("DUPLICATE LISTINGS CHECK (Across Files)")
print("="*80)

all_listing_ids = []
file_id_counts = {}

for csv_file, df in csv_data.items():
    if 'listing_id' in df.columns:
        ids = df['listing_id'].dropna().astype(str).tolist()
        all_listing_ids.extend(ids)
        file_id_counts[csv_file] = len(ids)

if all_listing_ids:
    total_listings = len(all_listing_ids)
    unique_listings = len(set(all_listing_ids))
    duplicates_across = total_listings - unique_listings

    print(f"\n📊 Total listings across all files: {total_listings:,}")
    print(f"📊 Unique listings: {unique_listings:,}")

    if duplicates_across > 0:
        print(f"⚠️  Duplicate listings across files: {duplicates_across:,}")

        # Find which IDs are duplicated
        id_counts = Counter(all_listing_ids)
        duplicated_ids = {id_: count for id_, count in id_counts.items() if count > 1}

        print(f"\n🔍 Number of listing IDs appearing multiple times: {len(duplicated_ids)}")

        # Show top 10 most duplicated
        if duplicated_ids:
            top_dupes = sorted(duplicated_ids.items(), key=lambda x: x[1], reverse=True)[:10]
            print("\nTop 10 most duplicated listing IDs:")
            for listing_id, count in top_dupes:
                print(f"  ID {listing_id}: appears {count} times")
    else:
        print("✅ No duplicate listings across files - All unique!")

# Summary
print("\n" + "="*80)
print("SUMMARY & RECOMMENDATIONS")
print("="*80)

print("\n📋 File Breakdown:")
for csv_file in sorted(csv_files):
    if csv_file in csv_data:
        df = csv_data[csv_file]
        print(f"  {csv_file}: {len(df):,} rows")

print(f"\n📊 Total rows if combined: {sum(len(df) for df in csv_data.values()):,}")
print(f"📊 Unique listings if combined: {unique_listings:,}")

if all_compatible and duplicates_across == 0:
    print("\n✅ RECOMMENDATION: Safe to combine - No issues found!")
    print("   All files have identical structure and no duplicates")
elif all_compatible and duplicates_across > 0:
    print(f"\n⚠️  RECOMMENDATION: Can combine with deduplication")
    print(f"   Need to remove {duplicates_across:,} duplicate entries")
elif not all_compatible:
    print("\n⚠️  RECOMMENDATION: Column alignment needed before combining")
    print("   Files have different column structures")

print("\n" + "="*80)
