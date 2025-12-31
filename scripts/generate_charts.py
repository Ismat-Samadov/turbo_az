#!/usr/bin/env python3
"""
Turbo.az Market Analysis - Business Intelligence Charts
Generates executive-level visualizations and strategic insights from vehicle listing data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set professional chart styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

# Define paths
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / 'data' / 'turbo_az_listings_combined_clean_20251231_090519.csv'
CHARTS_DIR = BASE_DIR / 'charts'

# Color palette for professional charts
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'danger': '#C73E1D',
    'info': '#457B9D',
    'warning': '#E76F51',
    'dark': '#4A5859'
}

def clean_price(price_str):
    """Extract numeric price from string format"""
    if pd.isna(price_str):
        return None
    price_str = str(price_str)
    price_str = price_str.replace('≈', '').replace('₼', '').replace(',', '').replace(' ', '').strip()
    try:
        return float(price_str)
    except:
        return None

def clean_mileage(mileage_str):
    """Extract numeric mileage from string format"""
    if pd.isna(mileage_str):
        return None
    mileage_str = str(mileage_str).replace('km', '').replace(',', '').replace(' ', '').strip()
    try:
        return float(mileage_str)
    except:
        return None

def load_and_prepare_data():
    """Load and prepare dataset for analysis"""
    print("Loading dataset...")
    df = pd.read_csv(DATA_FILE)

    print(f"Total listings loaded: {len(df):,}")

    # Clean price column
    df['price_clean'] = df['price_azn'].apply(clean_price)

    # Clean mileage column
    df['mileage_clean'] = df['mileage'].apply(clean_mileage)

    # Filter valid prices for meaningful analysis
    df_valid = df[(df['price_clean'] >= 1000) & (df['price_clean'] <= 500000)].copy()

    print(f"Listings with valid pricing: {len(df_valid):,}")

    return df, df_valid

def chart_01_price_distribution(df):
    """Chart 1: Price Distribution - Where is the market concentrated?"""
    plt.figure(figsize=(14, 6))

    bins = [0, 10000, 20000, 30000, 40000, 50000, 75000, 100000, 150000, 500000]
    labels = ['<10K', '10-20K', '20-30K', '30-40K', '40-50K', '50-75K', '75-100K', '100-150K', '>150K']

    df['price_range'] = pd.cut(df['price_clean'], bins=bins, labels=labels)
    price_counts = df['price_range'].value_counts().sort_index()

    ax = price_counts.plot(kind='bar', color=COLORS['primary'])
    plt.title('Market Inventory Distribution by Price Range', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Price Range (AZN)', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.xticks(rotation=45)

    for i, v in enumerate(price_counts):
        ax.text(i, v + 50, f'{v:,}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '01_price_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 01_price_distribution.png")

    return price_counts

def chart_02_brand_volume(df):
    """Chart 2: Top Brands - Market Leaders by Volume"""
    plt.figure(figsize=(14, 8))

    top_makes = df['make'].value_counts().head(15)

    ax = top_makes.plot(kind='barh', color=COLORS['secondary'])
    plt.title('Top 15 Brands by Market Share (Volume)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Number of Listings', fontsize=12)
    plt.ylabel('Brand', fontsize=12)

    for i, v in enumerate(top_makes):
        percentage = (v / len(df)) * 100
        ax.text(v + 20, i, f'{v:,} ({percentage:.1f}%)', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '02_brand_volume.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 02_brand_volume.png")

    return top_makes

def chart_03_brand_pricing(df):
    """Chart 3: Brand Positioning - Average Price by Brand"""
    plt.figure(figsize=(14, 8))

    top_makes = df['make'].value_counts().head(15).index
    brand_pricing = df[df['make'].isin(top_makes)].groupby('make')['price_clean'].mean().sort_values(ascending=True)

    ax = brand_pricing.plot(kind='barh', color=COLORS['accent'])
    plt.title('Brand Positioning: Average Listing Price', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Average Price (AZN)', fontsize=12)
    plt.ylabel('Brand', fontsize=12)

    for i, v in enumerate(brand_pricing):
        ax.text(v + 500, i, f'{v:,.0f} ₼', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '03_brand_pricing.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 03_brand_pricing.png")

    return brand_pricing

def chart_04_year_trends(df):
    """Chart 4: Vehicle Age Profile - Inventory by Model Year"""
    plt.figure(figsize=(14, 6))

    df_years = df[(df['year'] >= 2000) & (df['year'] <= 2025)]
    year_counts = df_years['year'].value_counts().sort_index()

    plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=2.5, color=COLORS['success'], markersize=6)
    plt.fill_between(year_counts.index, year_counts.values, alpha=0.3, color=COLORS['success'])

    plt.title('Inventory Distribution by Vehicle Age', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Model Year', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '04_year_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 04_year_trends.png")

    return year_counts

def chart_05_fuel_type_market(df):
    """Chart 5: Energy Source Distribution - Market Segmentation"""
    plt.figure(figsize=(14, 6))

    fuel_counts = df['fuel_type'].value_counts().head(8)

    ax = fuel_counts.plot(kind='bar', color=COLORS['danger'])
    plt.title('Market Segmentation by Fuel Type', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Fuel Type', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.xticks(rotation=45)

    total = fuel_counts.sum()
    for i, v in enumerate(fuel_counts):
        percentage = (v / total) * 100
        ax.text(i, v + 50, f'{v:,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '05_fuel_type_market.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 05_fuel_type_market.png")

    return fuel_counts

def chart_06_transmission_preference(df):
    """Chart 6: Transmission Technology - Customer Preferences"""
    plt.figure(figsize=(12, 6))

    trans_counts = df['transmission'].value_counts()

    ax = trans_counts.plot(kind='bar', color=COLORS['dark'])
    plt.title('Transmission Type Market Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Transmission Type', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.xticks(rotation=45)

    total = trans_counts.sum()
    for i, v in enumerate(trans_counts):
        percentage = (v / total) * 100
        ax.text(i, v + 100, f'{v:,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '06_transmission_preference.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 06_transmission_preference.png")

    return trans_counts

def chart_07_geographic_distribution(df):
    """Chart 7: Geographic Concentration - Where are the vehicles?"""
    plt.figure(figsize=(14, 6))

    city_counts = df['city'].value_counts().head(10)

    ax = city_counts.plot(kind='bar', color=COLORS['info'])
    plt.title('Geographic Distribution: Top 10 Cities', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.xticks(rotation=45)

    total = df.shape[0]
    for i, v in enumerate(city_counts):
        percentage = (v / total) * 100
        ax.text(i, v + 100, f'{v:,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '07_geographic_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 07_geographic_distribution.png")

    return city_counts

def chart_08_price_depreciation(df):
    """Chart 8: Value Retention - Price Trends by Vehicle Age"""
    plt.figure(figsize=(14, 6))

    df_years = df[(df['year'] >= 2005) & (df['year'] <= 2025)]
    year_price = df_years.groupby('year')['price_clean'].mean().sort_index()

    plt.plot(year_price.index, year_price.values, marker='o', linewidth=2.5, color=COLORS['danger'], markersize=8)
    plt.fill_between(year_price.index, year_price.values, alpha=0.2, color=COLORS['danger'])

    plt.title('Value Retention: Average Price by Model Year', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Model Year', fontsize=12)
    plt.ylabel('Average Price (AZN)', fontsize=12)
    plt.grid(True, alpha=0.3)

    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f} ₼'))

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '08_price_depreciation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 08_price_depreciation.png")

    return year_price

def chart_09_new_vs_used_market(df):
    """Chart 9: Market Composition - New vs Used Vehicles"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    new_used = df['is_new'].value_counts()
    new_used.index = ['Used', 'New']

    # Volume comparison
    axes[0].bar(new_used.index, new_used.values, color=[COLORS['info'], COLORS['warning']])
    axes[0].set_title('Inventory Composition: New vs Used', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Number of Listings', fontsize=11)

    for i, v in enumerate(new_used.values):
        percentage = (v / new_used.sum()) * 100
        axes[0].text(i, v + 100, f'{v:,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')

    # Price comparison
    price_comparison = df.groupby('is_new')['price_clean'].mean()
    price_comparison.index = ['Used', 'New']

    axes[1].bar(price_comparison.index, price_comparison.values, color=[COLORS['info'], COLORS['warning']])
    axes[1].set_title('Price Premium: New vs Used Vehicles', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Average Price (AZN)', fontsize=11)

    for i, v in enumerate(price_comparison.values):
        axes[1].text(i, v + 500, f'{v:,.0f} ₼', ha='center', va='bottom', fontweight='bold')

    plt.suptitle('New vs Used Vehicle Market Analysis', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '09_new_vs_used_market.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 09_new_vs_used_market.png")

    return new_used, price_comparison

def chart_10_mileage_profile(df):
    """Chart 10: Usage Patterns - Vehicle Mileage Distribution"""
    plt.figure(figsize=(14, 6))

    df_mileage = df[(df['mileage_clean'] > 0) & (df['mileage_clean'] <= 500000)].copy()
    df_mileage['mileage_k'] = df_mileage['mileage_clean'] / 1000

    bins = [0, 50, 100, 150, 200, 250, 300, 500]
    labels = ['0-50K', '50-100K', '100-150K', '150-200K', '200-250K', '250-300K', '>300K']

    df_mileage['mileage_range'] = pd.cut(df_mileage['mileage_k'], bins=bins, labels=labels)
    mileage_counts = df_mileage['mileage_range'].value_counts().sort_index()

    ax = mileage_counts.plot(kind='bar', color=COLORS['success'])
    plt.title('Vehicle Usage Profile: Distribution by Mileage', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Mileage Range (km)', fontsize=12)
    plt.ylabel('Number of Listings', fontsize=12)
    plt.xticks(rotation=45)

    for i, v in enumerate(mileage_counts):
        ax.text(i, v + 50, f'{v:,}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '10_mileage_profile.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 10_mileage_profile.png")

    return mileage_counts

def chart_11_premium_services(df):
    """Chart 11: Service Adoption - Premium Features Usage"""
    fig, ax = plt.subplots(figsize=(12, 6))

    feature_counts = pd.Series({
        'VIP Listings': df['is_vip'].sum(),
        'Featured Ads': df['is_featured'].sum(),
        'Salon Dealers': df['is_salon'].sum(),
        'Credit Available': df['has_credit'].sum(),
        'Barter Option': df['has_barter'].sum()
    })

    ax.barh(feature_counts.index, feature_counts.values, color=COLORS['warning'])
    plt.title('Premium Services & Features Adoption Rate', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Number of Listings', fontsize=12)

    total = df.shape[0]
    for i, v in enumerate(feature_counts.values):
        percentage = (v / total) * 100
        ax.text(v + 100, i, f'{v:,} ({percentage:.1f}%)', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '11_premium_services.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 11_premium_services.png")

    return feature_counts

def chart_12_market_concentration(df):
    """Chart 12: Competitive Landscape - Market Concentration"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Top 10 vs Others
    top_10_makes = df['make'].value_counts().head(10)
    other_makes = df['make'].value_counts()[10:].sum()

    market_share = pd.concat([top_10_makes, pd.Series({'Other Brands': other_makes})])

    axes[0].bar(range(len(market_share)), market_share.values, color=COLORS['dark'])
    axes[0].set_xticks(range(len(market_share)))
    axes[0].set_xticklabels(market_share.index, rotation=45, ha='right')
    axes[0].set_title('Market Fragmentation: Top 10 vs Others', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Number of Listings', fontsize=11)

    # Cumulative market share of top 5
    top_brands = df['make'].value_counts().head(5)
    total_listings = len(df)
    cumulative_pct = [(top_brands[:i+1].sum() / total_listings * 100) for i in range(len(top_brands))]

    axes[1].bar(range(len(top_brands)), top_brands.values, color=COLORS['success'], alpha=0.7)
    axes[1].set_xticks(range(len(top_brands)))
    axes[1].set_xticklabels(top_brands.index, rotation=45, ha='right')

    ax2 = axes[1].twinx()
    ax2.plot(range(len(top_brands)), cumulative_pct, color=COLORS['danger'], marker='o', linewidth=3, markersize=10)
    ax2.set_ylabel('Cumulative Market Share (%)', fontsize=11, color=COLORS['danger'])
    ax2.tick_params(axis='y', labelcolor=COLORS['danger'])

    axes[1].set_title('Top 5 Brands: Cumulative Dominance', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Number of Listings', fontsize=11)

    for i, pct in enumerate(cumulative_pct):
        ax2.text(i, pct + 1, f'{pct:.1f}%', ha='center', fontweight='bold', color=COLORS['danger'])

    plt.suptitle('Competitive Landscape Analysis', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '12_market_concentration.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 12_market_concentration.png")

    return market_share, cumulative_pct

def generate_business_insights(df, df_valid):
    """Generate executive-level business insights"""
    insights = {}

    # Market size
    insights['total_listings'] = len(df)
    insights['avg_price'] = df_valid['price_clean'].mean()
    insights['median_price'] = df_valid['price_clean'].median()
    insights['total_inventory_value'] = df_valid['price_clean'].sum()

    # Brand concentration
    insights['top_brand'] = df['make'].value_counts().index[0]
    insights['top_brand_count'] = df['make'].value_counts().values[0]
    insights['top_brand_share'] = (insights['top_brand_count'] / len(df)) * 100

    # Top 5 dominance
    top_5_count = df['make'].value_counts().head(5).sum()
    insights['top_5_share'] = (top_5_count / len(df)) * 100

    # Vehicle age
    insights['avg_year'] = df['year'].mean()
    insights['most_common_year'] = int(df['year'].mode()[0])
    insights['avg_vehicle_age'] = 2025 - insights['avg_year']

    # Fuel preferences
    insights['dominant_fuel'] = df['fuel_type'].value_counts().index[0]
    insights['dominant_fuel_share'] = (df['fuel_type'].value_counts().values[0] / len(df)) * 100

    # Green vehicles (Hybrid + Electric)
    green_vehicles = df[df['fuel_type'].str.contains('Hibrid|Elektro', case=False, na=False)].shape[0]
    insights['green_vehicle_count'] = green_vehicles
    insights['green_vehicle_share'] = (green_vehicles / len(df)) * 100

    # Transmission
    auto_count = df[df['transmission'].str.contains('Avtomat', case=False, na=False)].shape[0]
    insights['automatic_share'] = (auto_count / len(df)) * 100

    # Geographic concentration
    insights['top_city'] = df['city'].value_counts().index[0]
    insights['top_city_share'] = (df['city'].value_counts().values[0] / len(df)) * 100

    # New vs Used
    insights['new_count'] = int((df['is_new'] == True).sum())
    insights['used_count'] = int((df['is_new'] == False).sum())
    insights['new_share'] = (insights['new_count'] / len(df)) * 100
    insights['new_avg_price'] = df[df['is_new'] == True]['price_clean'].mean()
    insights['used_avg_price'] = df[df['is_new'] == False]['price_clean'].mean()
    insights['new_price_premium'] = ((insights['new_avg_price'] - insights['used_avg_price']) / insights['used_avg_price']) * 100

    # Premium services
    insights['vip_share'] = (df['is_vip'].sum() / len(df)) * 100
    insights['salon_share'] = (df['is_salon'].sum() / len(df)) * 100
    insights['credit_share'] = (df['has_credit'].sum() / len(df)) * 100
    insights['barter_share'] = (df['has_barter'].sum() / len(df)) * 100

    # Mileage insights
    df_mileage = df[df['mileage_clean'] > 0]
    insights['avg_mileage'] = df_mileage['mileage_clean'].mean()
    insights['median_mileage'] = df_mileage['mileage_clean'].median()

    # Price segments
    budget_count = df[df['price_clean'] < 10000].shape[0]
    economy_count = df[(df['price_clean'] >= 10000) & (df['price_clean'] < 25000)].shape[0]
    midrange_count = df[(df['price_clean'] >= 25000) & (df['price_clean'] < 50000)].shape[0]
    premium_count = df[(df['price_clean'] >= 50000) & (df['price_clean'] < 100000)].shape[0]
    luxury_count = df[df['price_clean'] >= 100000].shape[0]

    insights['budget_share'] = (budget_count / len(df_valid)) * 100
    insights['economy_share'] = (economy_count / len(df_valid)) * 100
    insights['midrange_share'] = (midrange_count / len(df_valid)) * 100
    insights['premium_share'] = (premium_count / len(df_valid)) * 100
    insights['luxury_share'] = (luxury_count / len(df_valid)) * 100

    return insights

def print_business_insights(insights):
    """Print executive summary of business insights"""
    print("\n" + "="*80)
    print("EXECUTIVE BUSINESS INSIGHTS - AZERBAIJAN AUTOMOTIVE MARKET")
    print("="*80)

    print(f"\n📊 MARKET SIZE & VALUE")
    print(f"   Active Listings: {insights['total_listings']:,}")
    print(f"   Total Inventory Value: {insights['total_inventory_value']:,.0f} AZN")
    print(f"   Average Vehicle Price: {insights['avg_price']:,.0f} AZN")
    print(f"   Median Vehicle Price: {insights['median_price']:,.0f} AZN")

    print(f"\n🏆 COMPETITIVE LANDSCAPE")
    print(f"   Market Leader: {insights['top_brand']} ({insights['top_brand_share']:.1f}% market share)")
    print(f"   Top 5 Brands Control: {insights['top_5_share']:.1f}% of total market")
    print(f"   Market Fragmentation: {insights['total_listings'] - int(insights['top_5_share']/100 * insights['total_listings']):,} listings from smaller brands")

    print(f"\n📅 VEHICLE AGE PROFILE")
    print(f"   Average Vehicle Age: {insights['avg_vehicle_age']:.1f} years")
    print(f"   Most Popular Year: {insights['most_common_year']}")
    print(f"   Average Model Year: {insights['avg_year']:.1f}")

    print(f"\n⛽ ENERGY SOURCE PREFERENCES")
    print(f"   Dominant Fuel Type: {insights['dominant_fuel']} ({insights['dominant_fuel_share']:.1f}%)")
    print(f"   Green Vehicles (Hybrid/Electric): {insights['green_vehicle_count']:,} ({insights['green_vehicle_share']:.1f}%)")
    print(f"   Automatic Transmission: {insights['automatic_share']:.1f}%")

    print(f"\n📍 GEOGRAPHIC CONCENTRATION")
    print(f"   Primary Market: {insights['top_city']} ({insights['top_city_share']:.1f}% of listings)")
    print(f"   Other Cities: {100 - insights['top_city_share']:.1f}%")

    print(f"\n🆕 INVENTORY COMPOSITION")
    print(f"   New Vehicles: {insights['new_count']:,} ({insights['new_share']:.1f}%)")
    print(f"   Used Vehicles: {insights['used_count']:,} ({100-insights['new_share']:.1f}%)")
    print(f"   New Vehicle Price Premium: +{insights['new_price_premium']:.1f}%")

    print(f"\n💰 PRICE SEGMENTATION")
    print(f"   Budget (<10K): {insights['budget_share']:.1f}%")
    print(f"   Economy (10-25K): {insights['economy_share']:.1f}%")
    print(f"   Mid-Range (25-50K): {insights['midrange_share']:.1f}%")
    print(f"   Premium (50-100K): {insights['premium_share']:.1f}%")
    print(f"   Luxury (100K+): {insights['luxury_share']:.1f}%")

    print(f"\n⭐ PREMIUM SERVICES ADOPTION")
    print(f"   VIP Listings: {insights['vip_share']:.1f}%")
    print(f"   Salon Dealers: {insights['salon_share']:.1f}%")
    print(f"   Credit Available: {insights['credit_share']:.1f}%")
    print(f"   Barter Accepted: {insights['barter_share']:.1f}%")

    print(f"\n🛣️  VEHICLE USAGE")
    print(f"   Average Mileage: {insights['avg_mileage']:,.0f} km")
    print(f"   Median Mileage: {insights['median_mileage']:,.0f} km")

    print("\n" + "="*80)

def main():
    """Main execution function"""
    print("="*80)
    print("AZERBAIJAN AUTOMOTIVE MARKET - BUSINESS INTELLIGENCE ANALYSIS")
    print("="*80)

    # Load data
    df, df_valid = load_and_prepare_data()

    print(f"\n📈 Generating business intelligence charts...")
    print("-" * 80)

    # Generate all charts
    chart_01_price_distribution(df_valid)
    chart_02_brand_volume(df)
    chart_03_brand_pricing(df_valid)
    chart_04_year_trends(df)
    chart_05_fuel_type_market(df)
    chart_06_transmission_preference(df)
    chart_07_geographic_distribution(df)
    chart_08_price_depreciation(df_valid)
    chart_09_new_vs_used_market(df)
    chart_10_mileage_profile(df)
    chart_11_premium_services(df)
    chart_12_market_concentration(df)

    print("-" * 80)
    print(f"✅ All charts generated successfully!")
    print(f"📁 Charts saved to: {CHARTS_DIR}")

    # Generate and print insights
    insights = generate_business_insights(df, df_valid)
    print_business_insights(insights)

    print("\n✅ Business analysis complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
