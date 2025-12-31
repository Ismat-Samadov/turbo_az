"""
Comprehensive verification of data combination
Double-check that no data was lost and combination is correct
"""
import pandas as pd
import os
import json

print("="*80)
print("COMPREHENSIVE DATA COMBINATION VERIFICATION")
print("="*80)

data_dir = "../data"

# Load original files
print("\n📥 STEP 1: Loading original CSV files...")
original_files = [
    'turbo_az_listings_20251224_083422.csv',
    'turbo_az_listings_20251224_110136.csv',
    'turbo_az_listings_20251231_072327.csv',
    'turbo_az_listings_20251231_072333.csv',
    'turbo_az_listings_combined_20251123_013059.csv'
]

original_dfs = {}
all_original_ids = set()

for filename in original_files:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, encoding='utf-8-sig', low_memory=False)
        original_dfs[filename] = df
        ids = set(df['listing_id'].astype(str).tolist())
        all_original_ids.update(ids)
        print(f"  ✓ {filename}: {len(df):,} rows, {len(ids):,} unique IDs")

print(f"\n  📊 Total unique listing IDs across all original files: {len(all_original_ids):,}")

# Load combined file
print("\n📥 STEP 2: Loading combined clean file...")
combined_file = 'turbo_az_listings_combined_clean_20251231_083705.csv'
combined_path = os.path.join(data_dir, combined_file)

if not os.path.exists(combined_path):
    print(f"  ❌ ERROR: Combined file not found!")
    exit(1)

combined_df = pd.read_csv(combined_path, encoding='utf-8-sig', low_memory=False)
combined_ids = set(combined_df['listing_id'].astype(str).tolist())

print(f"  ✓ {combined_file}: {len(combined_df):,} rows")
print(f"  ✓ Unique listing IDs in combined file: {len(combined_ids):,}")

# VERIFICATION 1: Check if all unique IDs from originals are in combined
print("\n" + "="*80)
print("🔍 VERIFICATION 1: Data Completeness Check")
print("="*80)

missing_ids = all_original_ids - combined_ids
extra_ids = combined_ids - all_original_ids

print(f"\n  Original unique IDs: {len(all_original_ids):,}")
print(f"  Combined unique IDs: {len(combined_ids):,}")
print(f"  Missing IDs: {len(missing_ids):,}")
print(f"  Extra IDs: {len(extra_ids):,}")

if len(missing_ids) > 0:
    print(f"\n  ❌ WARNING: {len(missing_ids)} IDs from original files are MISSING in combined!")
    print(f"     First 10 missing: {list(missing_ids)[:10]}")
else:
    print(f"\n  ✅ PASS: All original IDs are present in combined file")

if len(extra_ids) > 0:
    print(f"\n  ❌ WARNING: {len(extra_ids)} IDs in combined that weren't in originals!")
    print(f"     First 10 extra: {list(extra_ids)[:10]}")
else:
    print(f"  ✅ PASS: No extra IDs in combined file")

# VERIFICATION 2: Check for duplicates in combined file
print("\n" + "="*80)
print("🔍 VERIFICATION 2: Duplicate Check in Combined File")
print("="*80)

duplicate_ids = combined_df['listing_id'].duplicated().sum()
print(f"\n  Duplicate rows in combined file: {duplicate_ids:,}")

if duplicate_ids > 0:
    print(f"  ❌ FAIL: Found {duplicate_ids} duplicates in combined file!")
    dupes = combined_df[combined_df['listing_id'].duplicated(keep=False)]['listing_id'].value_counts()
    print(f"  Duplicate IDs: {dupes.head(10)}")
else:
    print(f"  ✅ PASS: No duplicates in combined file")

# VERIFICATION 3: Column integrity check
print("\n" + "="*80)
print("🔍 VERIFICATION 3: Column Integrity Check")
print("="*80)

# Get columns from first original file
first_original_cols = list(original_dfs[original_files[0]].columns)
combined_cols = list(combined_df.columns)

print(f"\n  Original columns: {len(first_original_cols)}")
print(f"  Combined columns: {len(combined_cols)}")

if first_original_cols == combined_cols:
    print(f"  ✅ PASS: Column structure is IDENTICAL")
else:
    missing_cols = set(first_original_cols) - set(combined_cols)
    extra_cols = set(combined_cols) - set(first_original_cols)

    if missing_cols:
        print(f"  ❌ FAIL: Missing columns: {missing_cols}")
    if extra_cols:
        print(f"  ❌ FAIL: Extra columns: {extra_cols}")

# VERIFICATION 4: Sample data integrity check
print("\n" + "="*80)
print("🔍 VERIFICATION 4: Sample Data Integrity Check")
print("="*80)

# Pick 5 random IDs and verify their data matches
sample_ids = list(all_original_ids)[:5]
integrity_pass = True

print(f"\n  Checking {len(sample_ids)} sample records...")

for listing_id in sample_ids:
    # Find in combined
    combined_row = combined_df[combined_df['listing_id'].astype(str) == listing_id]

    if len(combined_row) == 0:
        print(f"  ❌ ID {listing_id}: NOT FOUND in combined file")
        integrity_pass = False
        continue

    # Find in originals
    found_in_original = False
    for filename, df in original_dfs.items():
        original_rows = df[df['listing_id'].astype(str) == listing_id]
        if len(original_rows) > 0:
            found_in_original = True

            # Compare key fields
            combined_title = combined_row.iloc[0]['title']
            original_title = original_rows.iloc[0]['title']

            if combined_title == original_title:
                print(f"  ✅ ID {listing_id}: Data matches ('{combined_title[:50]}...')")
            else:
                print(f"  ❌ ID {listing_id}: Data MISMATCH!")
                print(f"     Combined: {combined_title}")
                print(f"     Original: {original_title}")
                integrity_pass = False
            break

    if not found_in_original:
        print(f"  ❌ ID {listing_id}: Not found in any original file!")
        integrity_pass = False

if integrity_pass:
    print(f"\n  ✅ PASS: Sample data integrity verified")
else:
    print(f"\n  ❌ FAIL: Data integrity issues detected")

# VERIFICATION 5: File size sanity check
print("\n" + "="*80)
print("🔍 VERIFICATION 5: File Size Sanity Check")
print("="*80)

combined_size = os.path.getsize(combined_path) / (1024*1024)
print(f"\n  Combined file size: {combined_size:.2f} MB")

# Calculate expected size (should be larger than largest original)
original_sizes = []
for filename in original_files:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath) / (1024*1024)
        original_sizes.append(size)

max_original = max(original_sizes)
print(f"  Largest original file: {max_original:.2f} MB")

if combined_size > max_original:
    print(f"  ✅ PASS: Combined file is larger than largest original (as expected)")
else:
    print(f"  ⚠️  WARNING: Combined file seems smaller than expected")

# VERIFICATION 6: Check JSON and XLSX consistency
print("\n" + "="*80)
print("🔍 VERIFICATION 6: Cross-Format Consistency Check")
print("="*80)

json_file = combined_file.replace('.csv', '.json')
xlsx_file = combined_file.replace('.csv', '.xlsx')

json_path = os.path.join(data_dir, json_file)
xlsx_path = os.path.join(data_dir, xlsx_file)

formats_consistent = True

# Check JSON
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    print(f"\n  JSON file: {len(json_data):,} records")
    if len(json_data) == len(combined_df):
        print(f"  ✅ PASS: JSON record count matches CSV")
    else:
        print(f"  ❌ FAIL: JSON has {len(json_data):,} records, CSV has {len(combined_df):,}")
        formats_consistent = False
else:
    print(f"  ⚠️  JSON file not found")

# Check XLSX
if os.path.exists(xlsx_path):
    xlsx_df = pd.read_excel(xlsx_path, sheet_name='Listings')
    print(f"\n  XLSX file: {len(xlsx_df):,} records")
    if len(xlsx_df) == len(combined_df):
        print(f"  ✅ PASS: XLSX record count matches CSV")
    else:
        print(f"  ❌ FAIL: XLSX has {len(xlsx_df):,} records, CSV has {len(combined_df):,}")
        formats_consistent = False
else:
    print(f"  ⚠️  XLSX file not found")

# FINAL VERDICT
print("\n" + "="*80)
print("🎯 FINAL VERIFICATION VERDICT")
print("="*80)

all_checks = []

# Check 1: Completeness
all_checks.append(("Data Completeness", len(missing_ids) == 0 and len(extra_ids) == 0))

# Check 2: No duplicates
all_checks.append(("No Duplicates", duplicate_ids == 0))

# Check 3: Column integrity
all_checks.append(("Column Integrity", first_original_cols == combined_cols))

# Check 4: Sample data
all_checks.append(("Sample Data Integrity", integrity_pass))

# Check 5: File size
all_checks.append(("File Size Sanity", combined_size > max_original))

# Check 6: Cross-format
all_checks.append(("Cross-Format Consistency", formats_consistent))

print("\n  VERIFICATION RESULTS:")
print("  " + "-"*76)

all_passed = True
for check_name, passed in all_checks:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {check_name:30} {status}")
    if not passed:
        all_passed = False

print("  " + "-"*76)

if all_passed:
    print("\n  " + "🎉 "*20)
    print("\n  ✅✅✅ ALL VERIFICATIONS PASSED - 100% CONFIDENT ✅✅✅")
    print("\n  " + "🎉 "*20)
    print("\n  The combined file is VERIFIED and safe to use!")
    print(f"\n  📁 Use file: {combined_file}")
else:
    print("\n  ❌❌❌ VERIFICATION FAILED ❌❌❌")
    print("\n  Some checks did not pass. Review the issues above.")

print("\n" + "="*80)
