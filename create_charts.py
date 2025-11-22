"""
Turbo.az Market Analysis - Chart Generation
Creates comprehensive visualizations of the car listing data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import re

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read data
print("Reading data...")
df = pd.read_csv('turbo_az_listings_combined_20251123_013059.csv')
print(f"Total listings: {len(df)}")

# Create charts directory
Path('charts').mkdir(exist_ok=True)

# Extract numeric price from price_azn column
def extract_price(price_str):
    """Extract numeric price from string like '25 800 ₼' or '≈ 113 900 ₼'"""
    if pd.isna(price_str):
        return np.nan
    # Remove ≈, ₼, and spaces, then convert to float
    price_clean = re.sub(r'[≈₼\s]', '', str(price_str))
    try:
        return float(price_clean)
    except:
        return np.nan

df['price_numeric'] = df['price_azn'].apply(extract_price)

# Extract numeric mileage
def extract_mileage(mileage_str):
    """Extract numeric mileage from string like '85 000 km'"""
    if pd.isna(mileage_str):
        return np.nan
    match = re.search(r'(\d[\d\s]*)', str(mileage_str))
    if match:
        try:
            return float(match.group(1).replace(' ', ''))
        except:
            return np.nan
    return np.nan

df['mileage_numeric'] = df['mileage'].apply(extract_mileage)

print("Creating charts...\n")

# Chart 1: Price Distribution
print("1. Price distribution...")
fig, ax = plt.subplots(figsize=(12, 6))
prices = df['price_numeric'].dropna()
prices_filtered = prices[prices <= 150000]  # Filter outliers for better visualization
ax.hist(prices_filtered, bins=50, edgecolor='black', alpha=0.7)
ax.set_xlabel('Price (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Price Distribution of Car Listings', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
median_price = prices.median()
ax.axvline(median_price, color='red', linestyle='--', linewidth=2, label=f'Median: {median_price:,.0f} AZN')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('charts/01_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 2: Top 15 Makes
print("2. Top 15 car makes...")
fig, ax = plt.subplots(figsize=(12, 8))
top_makes = df['make'].value_counts().head(15)
bars = ax.barh(range(len(top_makes)), top_makes.values, color=sns.color_palette("viridis", 15))
ax.set_yticks(range(len(top_makes)))
ax.set_yticklabels(top_makes.index, fontsize=11)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Car Brands by Listing Count', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, top_makes.values)):
    ax.text(value + 50, i, f'{value:,}', va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('charts/02_top_makes.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 3: Top 15 Models
print("3. Top 15 car models...")
fig, ax = plt.subplots(figsize=(12, 8))
top_models = df['model'].value_counts().head(15)
bars = ax.barh(range(len(top_models)), top_models.values, color=sns.color_palette("plasma", 15))
ax.set_yticks(range(len(top_models)))
ax.set_yticklabels(top_models.index, fontsize=11)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Car Models by Listing Count', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
for i, (bar, value) in enumerate(zip(bars, top_models.values)):
    ax.text(value + 20, i, f'{value:,}', va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('charts/03_top_models.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 4: Year Distribution
print("4. Year distribution...")
fig, ax = plt.subplots(figsize=(14, 6))
years = df['year'].astype(str).str.extract(r'(\d{4})')[0].astype(float).dropna()
year_counts = years.value_counts().sort_index()
year_counts = year_counts[year_counts.index >= 2000]  # Focus on 2000+
ax.bar(year_counts.index, year_counts.values, edgecolor='black', alpha=0.7, width=0.8)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Cars by Manufacturing Year (2000+)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('charts/04_year_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 5: Average Price by Make (Top 15)
print("5. Average price by make...")
fig, ax = plt.subplots(figsize=(12, 8))
avg_price_by_make = df.groupby('make')['price_numeric'].mean().sort_values(ascending=False).head(15)
bars = ax.barh(range(len(avg_price_by_make)), avg_price_by_make.values,
               color=sns.color_palette("coolwarm", 15))
ax.set_yticks(range(len(avg_price_by_make)))
ax.set_yticklabels(avg_price_by_make.index, fontsize=11)
ax.set_xlabel('Average Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Most Expensive Car Brands (Average Price)', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
for i, (bar, value) in enumerate(zip(bars, avg_price_by_make.values)):
    ax.text(value + 1000, i, f'{value:,.0f}', va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('charts/05_avg_price_by_make.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 6: Mileage vs Price
print("6. Mileage vs price scatter...")
fig, ax = plt.subplots(figsize=(12, 7))
scatter_df = df[['mileage_numeric', 'price_numeric']].dropna()
scatter_df = scatter_df[(scatter_df['price_numeric'] <= 200000) &
                        (scatter_df['mileage_numeric'] <= 500000)]
ax.scatter(scatter_df['mileage_numeric'], scatter_df['price_numeric'],
           alpha=0.3, s=10, c='steelblue')
ax.set_xlabel('Mileage (km)', fontsize=12, fontweight='bold')
ax.set_ylabel('Price (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Price vs Mileage Relationship', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/06_mileage_vs_price.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 7: Fuel Type Distribution
print("7. Fuel type distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
fuel_counts = df['fuel_type'].value_counts().head(8)
colors = sns.color_palette("Set2", len(fuel_counts))
wedges, texts, autotexts = ax.pie(fuel_counts.values, labels=fuel_counts.index, autopct='%1.1f%%',
                                    colors=colors, startangle=90, textprops={'fontsize': 10})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax.set_title('Distribution by Fuel Type', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/07_fuel_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 8: Transmission Type
print("8. Transmission type distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
trans_counts = df['transmission'].value_counts().head(6)
ax.bar(range(len(trans_counts)), trans_counts.values, color=sns.color_palette("muted", len(trans_counts)),
       edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(trans_counts)))
ax.set_xticklabels(trans_counts.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Distribution by Transmission Type', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
for i, value in enumerate(trans_counts.values):
    ax.text(i, value + 100, f'{value:,}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/08_transmission_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 9: Body Type Distribution
print("9. Body type distribution...")
fig, ax = plt.subplots(figsize=(12, 7))
body_counts = df['body_type'].value_counts().head(10)
bars = ax.barh(range(len(body_counts)), body_counts.values, color=sns.color_palette("rocket", 10))
ax.set_yticks(range(len(body_counts)))
ax.set_yticklabels(body_counts.index, fontsize=11)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Body Types', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
for i, (bar, value) in enumerate(zip(bars, body_counts.values)):
    ax.text(value + 30, i, f'{value:,}', va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('charts/09_body_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 10: New vs Used
print("10. New vs used distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
new_used = df['is_new'].map({'Bəli': 'New', 'Xeyr': 'Used'}).value_counts()
colors = ['#2ecc71', '#3498db']
wedges, texts, autotexts = ax.pie(new_used.values, labels=new_used.index, autopct='%1.1f%%',
                                    colors=colors, startangle=90, textprops={'fontsize': 12})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(14)
ax.set_title('New vs Used Cars', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/10_new_vs_used.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 11: Top Cities
print("11. Top cities...")
fig, ax = plt.subplots(figsize=(10, 6))
city_counts = df['city'].value_counts().head(10)
ax.bar(range(len(city_counts)), city_counts.values, color=sns.color_palette("cubehelix", len(city_counts)),
       edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(city_counts)))
ax.set_xticklabels(city_counts.index, rotation=45, ha='right', fontsize=11)
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Cities by Listing Count', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
for i, value in enumerate(city_counts.values):
    ax.text(i, value + 100, f'{value:,}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/11_top_cities.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 12: Listing Features (Badges)
print("12. Listing features (badges)...")
fig, ax = plt.subplots(figsize=(10, 6))
badges = {
    'VIP': df['is_vip'].sum(),
    'Featured': df['is_featured'].sum(),
    'Salon': df['is_salon'].sum(),
    'Credit Available': df['has_credit'].sum(),
    'Barter Available': df['has_barter'].sum(),
    'VIN Available': df['has_vin'].sum()
}
colors_badges = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#1abc9c']
ax.bar(badges.keys(), badges.values(), color=colors_badges, edgecolor='black', alpha=0.8)
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Listing Features and Badges', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')
for i, (key, value) in enumerate(badges.items()):
    ax.text(i, value + 50, f'{value:,}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/12_listing_features.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 13: Price Range Analysis
print("13. Price range analysis...")
fig, ax = plt.subplots(figsize=(12, 6))
price_ranges = pd.cut(df['price_numeric'].dropna(),
                      bins=[0, 10000, 20000, 30000, 50000, 75000, 100000, 200000, float('inf')],
                      labels=['<10K', '10-20K', '20-30K', '30-50K', '50-75K', '75-100K', '100-200K', '>200K'])
range_counts = price_ranges.value_counts().sort_index()
ax.bar(range(len(range_counts)), range_counts.values, color=sns.color_palette("Spectral", len(range_counts)),
       edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(range_counts)))
ax.set_xticklabels(range_counts.index, fontsize=11)
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_xlabel('Price Range (AZN)', fontsize=12, fontweight='bold')
ax.set_title('Distribution by Price Range', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
for i, value in enumerate(range_counts.values):
    ax.text(i, value + 30, f'{value:,}', ha='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/13_price_ranges.png', dpi=300, bbox_inches='tight')
plt.close()

# Chart 14: Market Summary Stats
print("14. Market summary statistics...")
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
stats_text = f"""
TURBO.AZ MARKET SUMMARY STATISTICS
{'='*50}

Total Listings: {len(df):,}

PRICE STATISTICS
Average Price: {df['price_numeric'].mean():,.0f} AZN
Median Price: {df['price_numeric'].median():,.0f} AZN
Min Price: {df['price_numeric'].min():,.0f} AZN
Max Price: {df['price_numeric'].max():,.0f} AZN

MILEAGE STATISTICS
Average Mileage: {df['mileage_numeric'].mean():,.0f} km
Median Mileage: {df['mileage_numeric'].median():,.0f} km

TOP 3 BRANDS
1. {top_makes.index[0]}: {top_makes.values[0]:,} listings
2. {top_makes.index[1]}: {top_makes.values[1]:,} listings
3. {top_makes.index[2]}: {top_makes.values[2]:,} listings

NEW vs USED
New Cars: {(df['is_new'] == 'Bəli').sum():,} ({(df['is_new'] == 'Bəli').sum()/len(df)*100:.1f}%)
Used Cars: {(df['is_new'] == 'Xeyr').sum():,} ({(df['is_new'] == 'Xeyr').sum()/len(df)*100:.1f}%)

LISTING FEATURES
Salon Listings: {df['is_salon'].sum():,}
Credit Available: {df['has_credit'].sum():,}
Barter Available: {df['has_barter'].sum():,}
"""
ax.text(0.5, 0.5, stats_text, ha='center', va='center', fontsize=11,
        family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
plt.tight_layout()
plt.savefig('charts/14_market_summary.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*60)
print("✓ All 14 charts created successfully!")
print("✓ Saved to: charts/ folder")
print("="*60)
