"""
Combine all CSV data files and remove duplicates
"""
import pandas as pd
import os
from datetime import datetime

print("="*80)
print("COMBINING DATA FILES WITH DEDUPLICATION")
print("="*80)

data_dir = "../data"

# Find all CSV files (exclude already combined files)
csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
csv_files = sorted(csv_files)

print(f"\n📁 Found {len(csv_files)} CSV files to process\n")

# Load all CSV files
all_dataframes = []

for csv_file in csv_files:
    filepath = os.path.join(data_dir, csv_file)
    print(f"📄 Loading: {csv_file}")

    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig', low_memory=False)
        print(f"   ✓ Loaded {len(df):,} rows")
        all_dataframes.append(df)
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Combine all dataframes
print(f"\n🔄 Combining {len(all_dataframes)} files...")
combined_df = pd.concat(all_dataframes, ignore_index=True)
print(f"✓ Combined total: {len(combined_df):,} rows")

# Remove duplicates based on listing_id
print(f"\n🧹 Removing duplicates based on 'listing_id'...")
initial_count = len(combined_df)

# Keep the most recent scrape (last occurrence) of each listing_id
combined_df = combined_df.drop_duplicates(subset=['listing_id'], keep='last')

final_count = len(combined_df)
removed_count = initial_count - final_count

print(f"   Before: {initial_count:,} rows")
print(f"   After:  {final_count:,} rows")
print(f"   Removed: {removed_count:,} duplicates")

# Sort by listing_id
print(f"\n📊 Sorting by listing_id...")
combined_df = combined_df.sort_values('listing_id').reset_index(drop=True)

# Generate output filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_csv = os.path.join(data_dir, f'turbo_az_listings_combined_clean_{timestamp}.csv')
output_xlsx = os.path.join(data_dir, f'turbo_az_listings_combined_clean_{timestamp}.xlsx')
output_json = os.path.join(data_dir, f'turbo_az_listings_combined_clean_{timestamp}.json')

# Save combined file as CSV
print(f"\n💾 Saving combined data...")
print(f"   CSV: {os.path.basename(output_csv)}")
combined_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
csv_size = os.path.getsize(output_csv) / (1024*1024)
print(f"   ✓ Saved ({csv_size:.2f} MB)")

# Save as Excel
print(f"   XLSX: {os.path.basename(output_xlsx)}")
with pd.ExcelWriter(output_xlsx, engine='openpyxl') as writer:
    combined_df.to_excel(writer, sheet_name='Listings', index=False)

    # Auto-adjust column widths
    from openpyxl.utils import get_column_letter
    worksheet = writer.sheets['Listings']
    for idx, col in enumerate(combined_df.columns):
        max_length = max(
            combined_df[col].astype(str).apply(len).max(),
            len(col)
        )
        col_letter = get_column_letter(idx + 1)
        worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)

xlsx_size = os.path.getsize(output_xlsx) / (1024*1024)
print(f"   ✓ Saved ({xlsx_size:.2f} MB)")

# Save as JSON
print(f"   JSON: {os.path.basename(output_json)}")
combined_df.to_json(output_json, orient='records', indent=2, force_ascii=False)
json_size = os.path.getsize(output_json) / (1024*1024)
print(f"   ✓ Saved ({json_size:.2f} MB)")

# Statistics
print("\n" + "="*80)
print("FINAL STATISTICS")
print("="*80)

print(f"\n📊 Combined Dataset:")
print(f"   Total unique listings: {final_count:,}")
print(f"   Total columns: {len(combined_df.columns)}")
print(f"   Duplicates removed: {removed_count:,}")
print(f"   Data quality: {(final_count / initial_count * 100):.1f}% unique")

# Show column info
print(f"\n📋 Data Columns ({len(combined_df.columns)}):")
for col in combined_df.columns:
    non_null = combined_df[col].notna().sum()
    completeness = (non_null / len(combined_df) * 100)
    print(f"   {col:25} - {completeness:5.1f}% complete")

# Show top makes
if 'make' in combined_df.columns:
    print(f"\n🚗 Top 10 Car Brands:")
    top_makes = combined_df['make'].value_counts().head(10)
    for make, count in top_makes.items():
        print(f"   {make:20} - {count:,} listings")

# Show price statistics
if 'price_azn' in combined_df.columns:
    print(f"\n💰 Price Analysis:")
    # Extract numeric prices
    prices = combined_df['price_azn'].str.extract(r'(\d+)')[0].astype(float)
    prices = prices.dropna()

    if len(prices) > 0:
        print(f"   Average: {prices.mean():,.0f} AZN")
        print(f"   Median:  {prices.median():,.0f} AZN")
        print(f"   Min:     {prices.min():,.0f} AZN")
        print(f"   Max:     {prices.max():,.0f} AZN")

print("\n" + "="*80)
print("✅ COMBINATION COMPLETE!")
print("="*80)
print(f"\n📁 Output files saved in: {data_dir}/")
print(f"   • {os.path.basename(output_csv)}")
print(f"   • {os.path.basename(output_xlsx)}")
print(f"   • {os.path.basename(output_json)}")
print("\n" + "="*80)
