"""
Turbo.az Market Analysis - Comparison Charts Generator
Compares car market data between two time periods and generates insightful visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import os
import re
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['figure.dpi'] = 150

# Color schemes
COLORS_OLD = '#3498db'  # Blue for old data
COLORS_NEW = '#e74c3c'  # Red for new data
COLORS_PALETTE = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c', '#34495e', '#e67e22']

# Output directory
CHARTS_DIR = 'charts'
os.makedirs(CHARTS_DIR, exist_ok=True)


def parse_price(price_str):
    """Convert price string to numeric value"""
    if pd.isna(price_str) or price_str == '':
        return None
    price_str = str(price_str)
    # Remove currency symbols and spaces
    price_str = price_str.replace('₼', '').replace('≈', '').replace(' ', '').strip()
    try:
        return float(price_str)
    except:
        return None


def parse_mileage(mileage_str):
    """Convert mileage string to numeric value"""
    if pd.isna(mileage_str) or mileage_str == '':
        return None
    mileage_str = str(mileage_str)
    # Extract numbers
    numbers = re.findall(r'[\d\s]+', mileage_str.replace(' ', ''))
    if numbers:
        try:
            return int(''.join(numbers[0].split()))
        except:
            return None
    return None


def parse_year(year_val):
    """Convert year to numeric"""
    if pd.isna(year_val):
        return None
    try:
        return int(year_val)
    except:
        return None


def parse_engine_volume(engine_str):
    """Convert engine volume string to numeric"""
    if pd.isna(engine_str) or engine_str == '':
        return None
    engine_str = str(engine_str)
    numbers = re.findall(r'[\d.]+', engine_str)
    if numbers:
        try:
            return float(numbers[0])
        except:
            return None
    return None


def load_and_prepare_data(old_file, new_file):
    """Load both CSV files and prepare data"""
    print(f"Loading old data from: {old_file}")
    df_old = pd.read_csv(old_file, encoding='utf-8-sig')
    print(f"  - Loaded {len(df_old)} records")

    print(f"Loading new data from: {new_file}")
    df_new = pd.read_csv(new_file, encoding='utf-8-sig')
    print(f"  - Loaded {len(df_new)} records")

    # Parse numeric fields
    for df in [df_old, df_new]:
        df['price_numeric'] = df['price_azn'].apply(parse_price)
        df['mileage_numeric'] = df['mileage'].apply(parse_mileage)
        df['year_numeric'] = df['year'].apply(parse_year)
        df['engine_numeric'] = df['engine_volume'].apply(parse_engine_volume)

    return df_old, df_new


def calculate_statistics(df, label):
    """Calculate key statistics for a dataset"""
    stats = {
        'label': label,
        'total_listings': len(df),
        'avg_price': df['price_numeric'].mean(),
        'median_price': df['price_numeric'].median(),
        'min_price': df['price_numeric'].min(),
        'max_price': df['price_numeric'].max(),
        'avg_mileage': df['mileage_numeric'].mean(),
        'median_mileage': df['mileage_numeric'].median(),
        'avg_year': df['year_numeric'].mean(),
        'new_cars_pct': (df['is_new'] == 'Bəli').sum() / len(df) * 100 if len(df) > 0 else 0,
        'salon_pct': (df['is_salon'] == True).sum() / len(df) * 100 if len(df) > 0 else 0,
        'credit_pct': (df['has_credit'] == True).sum() / len(df) * 100 if len(df) > 0 else 0,
        'barter_pct': (df['has_barter'] == True).sum() / len(df) * 100 if len(df) > 0 else 0,
    }
    return stats


def chart_01_market_overview(df_old, df_new, stats_old, stats_new):
    """Chart 1: Market Overview Comparison"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Market Overview: November 2025 vs December 2025', fontsize=18, fontweight='bold', y=1.02)

    # 1. Total Listings
    ax = axes[0, 0]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['total_listings'], stats_new['total_listings']],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('Total Listings', fontweight='bold')
    ax.set_ylabel('Number of Listings')
    for bar, val in zip(bars, [stats_old['total_listings'], stats_new['total_listings']]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                f'{val:,}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    change = ((stats_new['total_listings'] - stats_old['total_listings']) / stats_old['total_listings']) * 100
    ax.text(0.5, 0.95, f'Change: {change:+.1f}%', transform=ax.transAxes, ha='center',
            fontsize=11, color='green' if change > 0 else 'red', fontweight='bold')

    # 2. Average Price
    ax = axes[0, 1]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['avg_price'], stats_new['avg_price']],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('Average Price (AZN)', fontweight='bold')
    ax.set_ylabel('Price (AZN)')
    for bar, val in zip(bars, [stats_old['avg_price'], stats_new['avg_price']]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                f'{val:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    change = ((stats_new['avg_price'] - stats_old['avg_price']) / stats_old['avg_price']) * 100
    ax.text(0.5, 0.95, f'Change: {change:+.1f}%', transform=ax.transAxes, ha='center',
            fontsize=11, color='green' if change < 0 else 'red', fontweight='bold')

    # 3. Median Price
    ax = axes[0, 2]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['median_price'], stats_new['median_price']],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('Median Price (AZN)', fontweight='bold')
    ax.set_ylabel('Price (AZN)')
    for bar, val in zip(bars, [stats_old['median_price'], stats_new['median_price']]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300,
                f'{val:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    change = ((stats_new['median_price'] - stats_old['median_price']) / stats_old['median_price']) * 100
    ax.text(0.5, 0.95, f'Change: {change:+.1f}%', transform=ax.transAxes, ha='center',
            fontsize=11, color='green' if change < 0 else 'red', fontweight='bold')

    # 4. Average Mileage
    ax = axes[1, 0]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['avg_mileage']/1000, stats_new['avg_mileage']/1000],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('Average Mileage (x1000 km)', fontweight='bold')
    ax.set_ylabel('Mileage (x1000 km)')
    for bar, val in zip(bars, [stats_old['avg_mileage']/1000, stats_new['avg_mileage']/1000]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val:,.0f}k', ha='center', va='bottom', fontweight='bold', fontsize=12)

    # 5. New Cars Percentage
    ax = axes[1, 1]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['new_cars_pct'], stats_new['new_cars_pct']],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('New Cars Percentage', fontweight='bold')
    ax.set_ylabel('Percentage (%)')
    for bar, val in zip(bars, [stats_old['new_cars_pct'], stats_new['new_cars_pct']]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

    # 6. Credit Availability
    ax = axes[1, 2]
    bars = ax.bar(['November 2025', 'December 2025'],
                  [stats_old['credit_pct'], stats_new['credit_pct']],
                  color=[COLORS_OLD, COLORS_NEW], edgecolor='black', linewidth=1.5)
    ax.set_title('Credit Available (%)', fontweight='bold')
    ax.set_ylabel('Percentage (%)')
    for bar, val in zip(bars, [stats_old['credit_pct'], stats_new['credit_pct']]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/01_market_overview_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 01_market_overview_comparison.png")


def chart_02_price_distribution(df_old, df_new):
    """Chart 2: Price Distribution Comparison"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Price Distribution Comparison', fontsize=16, fontweight='bold')

    # Filter valid prices
    prices_old = df_old['price_numeric'].dropna()
    prices_new = df_new['price_numeric'].dropna()

    # Limit to reasonable range for visualization
    max_price = 200000
    prices_old = prices_old[prices_old <= max_price]
    prices_new = prices_new[prices_new <= max_price]

    # Histogram comparison
    ax = axes[0]
    bins = np.arange(0, max_price + 10000, 10000)
    ax.hist(prices_old, bins=bins, alpha=0.6, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.hist(prices_new, bins=bins, alpha=0.6, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xlabel('Price (AZN)')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Price Distribution Histogram')
    ax.legend()
    ax.set_xlim(0, max_price)

    # Box plot comparison
    ax = axes[1]
    box_data = [prices_old, prices_new]
    bp = ax.boxplot(box_data, labels=['November 2025', 'December 2025'], patch_artist=True)
    bp['boxes'][0].set_facecolor(COLORS_OLD)
    bp['boxes'][1].set_facecolor(COLORS_NEW)
    ax.set_ylabel('Price (AZN)')
    ax.set_title('Price Distribution Box Plot')

    # Add median annotations
    medians = [np.median(prices_old), np.median(prices_new)]
    for i, median in enumerate(medians):
        ax.text(i + 1.15, median, f'{median:,.0f} AZN', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/02_price_distribution_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 02_price_distribution_comparison.png")


def chart_03_top_makes_comparison(df_old, df_new):
    """Chart 3: Top Car Makes Comparison"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle('Top Car Makes: Market Share Comparison', fontsize=16, fontweight='bold')

    # Get top 10 makes from combined data
    all_makes = pd.concat([df_old['make'], df_new['make']]).value_counts().head(15).index.tolist()

    # Count for each period
    makes_old = df_old['make'].value_counts()
    makes_new = df_new['make'].value_counts()

    # Prepare data for top makes
    top_makes = all_makes[:10]
    counts_old = [makes_old.get(make, 0) for make in top_makes]
    counts_new = [makes_new.get(make, 0) for make in top_makes]

    # Bar chart comparison
    ax = axes[0]
    x = np.arange(len(top_makes))
    width = 0.35
    bars1 = ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    bars2 = ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xlabel('Car Make')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Top 10 Car Makes - Listing Count')
    ax.set_xticks(x)
    ax.set_xticklabels(top_makes, rotation=45, ha='right')
    ax.legend()

    # Percentage change chart
    ax = axes[1]
    pct_changes = []
    for old, new in zip(counts_old, counts_new):
        if old > 0:
            pct_changes.append(((new - old) / old) * 100)
        else:
            pct_changes.append(100 if new > 0 else 0)

    colors = ['green' if x >= 0 else 'red' for x in pct_changes]
    bars = ax.barh(top_makes, pct_changes, color=colors, edgecolor='black')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Percentage Change (%)')
    ax.set_title('Listing Count Change by Make')

    # Add value labels
    for bar, val in zip(bars, pct_changes):
        x_pos = bar.get_width() + 1 if val >= 0 else bar.get_width() - 1
        ha = 'left' if val >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:+.1f}%',
                va='center', ha=ha, fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/03_top_makes_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 03_top_makes_comparison.png")


def chart_04_avg_price_by_make(df_old, df_new):
    """Chart 4: Average Price by Make Comparison"""
    fig, ax = plt.subplots(figsize=(16, 10))

    # Get top makes by volume
    all_makes = pd.concat([df_old['make'], df_new['make']]).value_counts().head(12).index.tolist()

    # Calculate average prices
    avg_old = df_old.groupby('make')['price_numeric'].mean()
    avg_new = df_new.groupby('make')['price_numeric'].mean()

    makes = all_makes
    prices_old = [avg_old.get(make, 0) for make in makes]
    prices_new = [avg_new.get(make, 0) for make in makes]

    x = np.arange(len(makes))
    width = 0.35

    bars1 = ax.bar(x - width/2, prices_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    bars2 = ax.bar(x + width/2, prices_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')

    ax.set_xlabel('Car Make')
    ax.set_ylabel('Average Price (AZN)')
    ax.set_title('Average Price by Top Car Makes', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(makes, rotation=45, ha='right')
    ax.legend()

    # Add percentage change annotations
    for i, (old, new) in enumerate(zip(prices_old, prices_new)):
        if old > 0:
            change = ((new - old) / old) * 100
            color = 'green' if change < 0 else 'red'
            ax.text(i, max(old, new) + 2000, f'{change:+.1f}%', ha='center',
                    fontsize=9, color=color, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/04_avg_price_by_make.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 04_avg_price_by_make.png")


def chart_05_fuel_type_trends(df_old, df_new):
    """Chart 5: Fuel Type Distribution Trends"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Fuel Type Distribution: November vs December 2025', fontsize=16, fontweight='bold')

    # Get fuel type counts
    fuel_old = df_old['fuel_type'].value_counts()
    fuel_new = df_new['fuel_type'].value_counts()

    all_fuels = list(set(fuel_old.index.tolist() + fuel_new.index.tolist()))
    all_fuels = [f for f in all_fuels if pd.notna(f) and f != '']

    # Get common fuel types
    fuels = fuel_old.head(6).index.tolist()
    counts_old = [fuel_old.get(f, 0) for f in fuels]
    counts_new = [fuel_new.get(f, 0) for f in fuels]

    # Bar chart - counts
    ax = axes[0]
    x = np.arange(len(fuels))
    width = 0.35
    ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(fuels, rotation=45, ha='right')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Fuel Type Count Comparison')
    ax.legend()

    # Bar chart - percentages
    ax = axes[1]
    total_old = sum(counts_old)
    total_new = sum(counts_new)
    pct_old = [(c / total_old * 100) if total_old > 0 else 0 for c in counts_old]
    pct_new = [(c / total_new * 100) if total_new > 0 else 0 for c in counts_new]

    ax.bar(x - width/2, pct_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, pct_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(fuels, rotation=45, ha='right')
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Fuel Type Market Share')
    ax.legend()

    # Change bar chart
    ax = axes[2]
    pct_changes = []
    for old, new in zip(counts_old, counts_new):
        if old > 0:
            pct_changes.append(((new - old) / old) * 100)
        else:
            pct_changes.append(100 if new > 0 else 0)

    colors = ['green' if x >= 0 else 'red' for x in pct_changes]
    bars = ax.bar(fuels, pct_changes, color=colors, edgecolor='black')
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_xticklabels(fuels, rotation=45, ha='right')
    ax.set_ylabel('Percentage Change (%)')
    ax.set_title('Fuel Type Change')

    for bar, val in zip(bars, pct_changes):
        y_pos = bar.get_height() + 2 if val >= 0 else bar.get_height() - 5
        ax.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val:+.1f}%',
                ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/05_fuel_type_trends.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 05_fuel_type_trends.png")


def chart_06_transmission_trends(df_old, df_new):
    """Chart 6: Transmission Type Trends"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Transmission Type Distribution', fontsize=16, fontweight='bold')

    trans_old = df_old['transmission'].value_counts()
    trans_new = df_new['transmission'].value_counts()

    all_trans = list(set(trans_old.index.tolist() + trans_new.index.tolist()))
    all_trans = [t for t in all_trans if pd.notna(t) and t != ''][:5]

    counts_old = [trans_old.get(t, 0) for t in all_trans]
    counts_new = [trans_new.get(t, 0) for t in all_trans]

    # Grouped bar
    ax = axes[0]
    x = np.arange(len(all_trans))
    width = 0.35
    ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(all_trans, rotation=30, ha='right')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Transmission Type Count')
    ax.legend()

    # Percentage comparison
    ax = axes[1]
    pct_old = [(c / sum(counts_old)) * 100 for c in counts_old]
    pct_new = [(c / sum(counts_new)) * 100 for c in counts_new]

    ax.bar(x - width/2, pct_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, pct_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(all_trans, rotation=30, ha='right')
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Transmission Type Share')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/06_transmission_trends.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 06_transmission_trends.png")


def chart_07_body_type_analysis(df_old, df_new):
    """Chart 7: Body Type Analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Body Type Distribution Analysis', fontsize=16, fontweight='bold')

    body_old = df_old['body_type'].value_counts().head(8)
    body_new = df_new['body_type'].value_counts().head(8)

    all_bodies = list(set(body_old.index.tolist() + body_new.index.tolist()))[:8]

    counts_old = [body_old.get(b, 0) for b in all_bodies]
    counts_new = [body_new.get(b, 0) for b in all_bodies]

    # Horizontal bar comparison
    ax = axes[0]
    y = np.arange(len(all_bodies))
    height = 0.35
    ax.barh(y - height/2, counts_old, height, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.barh(y + height/2, counts_new, height, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_yticks(y)
    ax.set_yticklabels(all_bodies)
    ax.set_xlabel('Number of Listings')
    ax.set_title('Body Type Listing Count')
    ax.legend()

    # Market share change
    ax = axes[1]
    total_old = sum(counts_old)
    total_new = sum(counts_new)
    share_old = [(c / total_old) * 100 for c in counts_old]
    share_new = [(c / total_new) * 100 for c in counts_new]
    share_change = [new - old for old, new in zip(share_old, share_new)]

    colors = ['green' if x >= 0 else 'red' for x in share_change]
    ax.barh(all_bodies, share_change, color=colors, edgecolor='black')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Market Share Change (percentage points)')
    ax.set_title('Body Type Market Share Change')

    for i, (body, change) in enumerate(zip(all_bodies, share_change)):
        x_pos = change + 0.1 if change >= 0 else change - 0.1
        ha = 'left' if change >= 0 else 'right'
        ax.text(x_pos, i, f'{change:+.2f}pp', va='center', ha=ha, fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/07_body_type_analysis.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 07_body_type_analysis.png")


def chart_08_year_distribution(df_old, df_new):
    """Chart 8: Year Distribution Analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Vehicle Age Distribution', fontsize=16, fontweight='bold')

    years_old = df_old['year_numeric'].dropna()
    years_new = df_new['year_numeric'].dropna()

    # Histogram
    ax = axes[0]
    bins = range(2000, 2027)
    ax.hist(years_old, bins=bins, alpha=0.6, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.hist(years_new, bins=bins, alpha=0.6, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xlabel('Manufacturing Year')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Year Distribution')
    ax.legend()

    # Age group comparison
    ax = axes[1]
    current_year = 2025

    def get_age_group(year):
        age = current_year - year
        if age <= 2:
            return 'New (0-2 yrs)'
        elif age <= 5:
            return 'Recent (3-5 yrs)'
        elif age <= 10:
            return 'Mid-age (6-10 yrs)'
        elif age <= 15:
            return 'Older (11-15 yrs)'
        else:
            return 'Classic (15+ yrs)'

    age_order = ['New (0-2 yrs)', 'Recent (3-5 yrs)', 'Mid-age (6-10 yrs)', 'Older (11-15 yrs)', 'Classic (15+ yrs)']

    df_old['age_group'] = df_old['year_numeric'].apply(lambda x: get_age_group(x) if pd.notna(x) else None)
    df_new['age_group'] = df_new['year_numeric'].apply(lambda x: get_age_group(x) if pd.notna(x) else None)

    age_old = df_old['age_group'].value_counts()
    age_new = df_new['age_group'].value_counts()

    counts_old = [age_old.get(a, 0) for a in age_order]
    counts_new = [age_new.get(a, 0) for a in age_order]

    x = np.arange(len(age_order))
    width = 0.35
    ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(age_order, rotation=30, ha='right')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Vehicle Age Group Distribution')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/08_year_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 08_year_distribution.png")


def chart_09_city_distribution(df_old, df_new):
    """Chart 9: City Distribution Analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Geographic Distribution of Listings', fontsize=16, fontweight='bold')

    city_old = df_old['city'].value_counts().head(10)
    city_new = df_new['city'].value_counts().head(10)

    all_cities = list(set(city_old.index.tolist() + city_new.index.tolist()))[:10]

    counts_old = [city_old.get(c, 0) for c in all_cities]
    counts_new = [city_new.get(c, 0) for c in all_cities]

    # Horizontal bar comparison
    ax = axes[0]
    y = np.arange(len(all_cities))
    height = 0.35
    ax.barh(y - height/2, counts_old, height, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.barh(y + height/2, counts_new, height, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_yticks(y)
    ax.set_yticklabels(all_cities)
    ax.set_xlabel('Number of Listings')
    ax.set_title('Top Cities by Listing Count')
    ax.legend()

    # Market concentration (bar comparison)
    ax = axes[1]
    baku_old = city_old.get('Bakı', 0)
    baku_new = city_new.get('Bakı', 0)

    total_old = df_old['city'].notna().sum()
    total_new = df_new['city'].notna().sum()

    baku_pct_old = (baku_old / total_old * 100) if total_old > 0 else 0
    baku_pct_new = (baku_new / total_new * 100) if total_new > 0 else 0

    x = np.arange(2)
    width = 0.35
    ax.bar(x - width/2, [baku_pct_old, 100-baku_pct_old], width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, [baku_pct_new, 100-baku_pct_new], width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(['Baku', 'Other Cities'])
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Baku vs Other Cities Market Share')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/09_city_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 09_city_distribution.png")


def chart_10_price_segments(df_old, df_new):
    """Chart 10: Price Segment Analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Price Segment Analysis', fontsize=16, fontweight='bold')

    def get_price_segment(price):
        if pd.isna(price):
            return None
        if price < 10000:
            return 'Budget (<10K)'
        elif price < 25000:
            return 'Economy (10-25K)'
        elif price < 50000:
            return 'Mid-range (25-50K)'
        elif price < 100000:
            return 'Premium (50-100K)'
        else:
            return 'Luxury (100K+)'

    segment_order = ['Budget (<10K)', 'Economy (10-25K)', 'Mid-range (25-50K)', 'Premium (50-100K)', 'Luxury (100K+)']

    df_old['price_segment'] = df_old['price_numeric'].apply(get_price_segment)
    df_new['price_segment'] = df_new['price_numeric'].apply(get_price_segment)

    seg_old = df_old['price_segment'].value_counts()
    seg_new = df_new['price_segment'].value_counts()

    counts_old = [seg_old.get(s, 0) for s in segment_order]
    counts_new = [seg_new.get(s, 0) for s in segment_order]

    # Bar comparison
    ax = axes[0]
    x = np.arange(len(segment_order))
    width = 0.35
    ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(segment_order, rotation=30, ha='right')
    ax.set_ylabel('Number of Listings')
    ax.set_title('Price Segment Distribution')
    ax.legend()

    # Percentage change
    ax = axes[1]
    pct_changes = []
    for old, new in zip(counts_old, counts_new):
        if old > 0:
            pct_changes.append(((new - old) / old) * 100)
        else:
            pct_changes.append(100 if new > 0 else 0)

    colors = ['green' if x >= 0 else 'red' for x in pct_changes]
    bars = ax.bar(segment_order, pct_changes, color=colors, edgecolor='black')
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_ylabel('Percentage Change (%)')
    ax.set_title('Price Segment Growth/Decline')
    ax.set_xticklabels(segment_order, rotation=30, ha='right')

    for bar, val in zip(bars, pct_changes):
        y_pos = bar.get_height() + 1 if val >= 0 else bar.get_height() - 3
        ax.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val:+.1f}%',
                ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/10_price_segments.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 10_price_segments.png")


def chart_11_listing_features(df_old, df_new):
    """Chart 11: Listing Features Comparison"""
    fig, ax = plt.subplots(figsize=(14, 8))

    features = ['is_salon', 'has_credit', 'has_barter', 'is_vip', 'is_featured', 'has_vin']
    feature_labels = ['Salon Seller', 'Credit Available', 'Barter Available', 'VIP Listing', 'Featured', 'VIN Check']

    pct_old = []
    pct_new = []

    for feat in features:
        pct_old.append((df_old[feat] == True).sum() / len(df_old) * 100)
        pct_new.append((df_new[feat] == True).sum() / len(df_new) * 100)

    x = np.arange(len(feature_labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, pct_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    bars2 = ax.bar(x + width/2, pct_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')

    ax.set_ylabel('Percentage of Listings (%)')
    ax.set_title('Listing Features Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(feature_labels, rotation=30, ha='right')
    ax.legend()

    # Add value labels
    for bar, val in zip(bars1, pct_old):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%',
                ha='center', fontsize=9)
    for bar, val in zip(bars2, pct_new):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%',
                ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/11_listing_features.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 11_listing_features.png")


def chart_12_mileage_vs_price(df_old, df_new):
    """Chart 12: Mileage vs Price Analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Mileage vs Price Relationship', fontsize=16, fontweight='bold')

    # Filter valid data
    old_valid = df_old[['price_numeric', 'mileage_numeric']].dropna()
    new_valid = df_new[['price_numeric', 'mileage_numeric']].dropna()

    # Limit to reasonable ranges
    old_valid = old_valid[(old_valid['price_numeric'] <= 150000) & (old_valid['mileage_numeric'] <= 400000)]
    new_valid = new_valid[(new_valid['price_numeric'] <= 150000) & (new_valid['mileage_numeric'] <= 400000)]

    # Scatter plots
    ax = axes[0]
    ax.scatter(old_valid['mileage_numeric']/1000, old_valid['price_numeric']/1000,
               alpha=0.3, s=20, c=COLORS_OLD, label='November 2025')
    ax.set_xlabel('Mileage (x1000 km)')
    ax.set_ylabel('Price (x1000 AZN)')
    ax.set_title('November 2025')
    ax.legend()

    ax = axes[1]
    ax.scatter(new_valid['mileage_numeric']/1000, new_valid['price_numeric']/1000,
               alpha=0.3, s=20, c=COLORS_NEW, label='December 2025')
    ax.set_xlabel('Mileage (x1000 km)')
    ax.set_ylabel('Price (x1000 AZN)')
    ax.set_title('December 2025')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/12_mileage_vs_price.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 12_mileage_vs_price.png")


def chart_13_color_trends(df_old, df_new):
    """Chart 13: Color Preferences"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Color Preferences Analysis', fontsize=16, fontweight='bold')

    color_old = df_old['color'].value_counts().head(10)
    color_new = df_new['color'].value_counts().head(10)

    all_colors = list(set(color_old.index.tolist() + color_new.index.tolist()))[:10]

    counts_old = [color_old.get(c, 0) for c in all_colors]
    counts_new = [color_new.get(c, 0) for c in all_colors]

    # Bar chart
    ax = axes[0]
    y = np.arange(len(all_colors))
    height = 0.35
    ax.barh(y - height/2, counts_old, height, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.barh(y + height/2, counts_new, height, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_yticks(y)
    ax.set_yticklabels(all_colors)
    ax.set_xlabel('Number of Listings')
    ax.set_title('Top Colors by Count')
    ax.legend()

    # Change analysis
    ax = axes[1]
    pct_changes = []
    for old, new in zip(counts_old, counts_new):
        if old > 0:
            pct_changes.append(((new - old) / old) * 100)
        else:
            pct_changes.append(0)

    colors_chart = ['green' if x >= 0 else 'red' for x in pct_changes]
    ax.barh(all_colors, pct_changes, color=colors_chart, edgecolor='black')
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Percentage Change (%)')
    ax.set_title('Color Preference Changes')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/13_color_trends.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 13_color_trends.png")


def chart_14_new_vs_used(df_old, df_new):
    """Chart 14: New vs Used Cars Analysis"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('New vs Used Cars Analysis', fontsize=16, fontweight='bold')

    # Count new vs used
    new_old = (df_old['is_new'] == 'Bəli').sum()
    used_old = (df_old['is_new'] == 'Xeyr').sum()
    new_new = (df_new['is_new'] == 'Bəli').sum()
    used_new = (df_new['is_new'] == 'Xeyr').sum()

    categories = ['New Cars', 'Used Cars']
    counts_old = [new_old, used_old]
    counts_new = [new_new, used_new]

    # Bar chart - counts
    ax = axes[0]
    x = np.arange(len(categories))
    width = 0.35
    ax.bar(x - width/2, counts_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, counts_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Number of Listings')
    ax.set_title('New vs Used Count')
    ax.legend()

    # Bar chart - percentages
    ax = axes[1]
    total_old = sum(counts_old)
    total_new = sum(counts_new)
    pct_old = [(c / total_old * 100) if total_old > 0 else 0 for c in counts_old]
    pct_new = [(c / total_new * 100) if total_new > 0 else 0 for c in counts_new]

    ax.bar(x - width/2, pct_old, width, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.bar(x + width/2, pct_new, width, label='December 2025', color=COLORS_NEW, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Percentage (%)')
    ax.set_title('New vs Used Market Share')
    ax.legend()

    # Add value labels
    for i, (old_pct, new_pct) in enumerate(zip(pct_old, pct_new)):
        ax.text(i - width/2, old_pct + 1, f'{old_pct:.1f}%', ha='center', fontsize=9)
        ax.text(i + width/2, new_pct + 1, f'{new_pct:.1f}%', ha='center', fontsize=9)

    # Change comparison bar
    ax = axes[2]
    pct_changes = []
    for old, new in zip(counts_old, counts_new):
        if old > 0:
            pct_changes.append(((new - old) / old) * 100)
        else:
            pct_changes.append(100 if new > 0 else 0)

    colors = ['green' if x >= 0 else 'red' for x in pct_changes]
    bars = ax.bar(categories, pct_changes, color=colors, edgecolor='black')
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_ylabel('Percentage Change (%)')
    ax.set_title('New vs Used Change')

    for bar, val in zip(bars, pct_changes):
        y_pos = bar.get_height() + 2 if val >= 0 else bar.get_height() - 5
        ax.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val:+.1f}%',
                ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/14_new_vs_used.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 14_new_vs_used.png")


def chart_15_top_models(df_old, df_new):
    """Chart 15: Top Models Analysis"""
    fig, ax = plt.subplots(figsize=(16, 10))

    # Create make-model combination
    df_old['make_model'] = df_old['make'] + ' ' + df_old['model'].fillna('')
    df_new['make_model'] = df_new['make'] + ' ' + df_new['model'].fillna('')

    models_old = df_old['make_model'].value_counts().head(15)
    models_new = df_new['make_model'].value_counts().head(15)

    all_models = list(set(models_old.index.tolist() + models_new.index.tolist()))[:15]

    counts_old = [models_old.get(m, 0) for m in all_models]
    counts_new = [models_new.get(m, 0) for m in all_models]

    y = np.arange(len(all_models))
    height = 0.35

    ax.barh(y - height/2, counts_old, height, label='November 2025', color=COLORS_OLD, edgecolor='black')
    ax.barh(y + height/2, counts_new, height, label='December 2025', color=COLORS_NEW, edgecolor='black')

    ax.set_yticks(y)
    ax.set_yticklabels(all_models)
    ax.set_xlabel('Number of Listings')
    ax.set_title('Top 15 Models Comparison', fontsize=14, fontweight='bold')
    ax.legend()

    plt.tight_layout()
    plt.savefig(f'{CHARTS_DIR}/15_top_models.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 15_top_models.png")


def chart_16_market_summary(stats_old, stats_new, df_old, df_new):
    """Chart 16: Market Summary Dashboard"""
    fig = plt.figure(figsize=(20, 14))
    fig.suptitle('Azerbaijan Car Market Summary: November vs December 2025',
                 fontsize=20, fontweight='bold', y=0.98)

    # Create grid
    gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)

    # Key metrics
    metrics = [
        ('Total Listings', stats_old['total_listings'], stats_new['total_listings'], False),
        ('Average Price (AZN)', stats_old['avg_price'], stats_new['avg_price'], True),
        ('Median Price (AZN)', stats_old['median_price'], stats_new['median_price'], True),
        ('Avg Mileage (km)', stats_old['avg_mileage'], stats_new['avg_mileage'], True),
    ]

    for i, (label, old_val, new_val, is_price) in enumerate(metrics):
        ax = fig.add_subplot(gs[0, i])

        change = ((new_val - old_val) / old_val) * 100 if old_val != 0 else 0
        color = 'green' if (change < 0 and is_price) or (change > 0 and not is_price) else 'red'

        ax.text(0.5, 0.7, label, ha='center', va='center', fontsize=12, fontweight='bold',
                transform=ax.transAxes)
        ax.text(0.5, 0.4, f'{new_val:,.0f}', ha='center', va='center', fontsize=24, fontweight='bold',
                transform=ax.transAxes)
        ax.text(0.5, 0.15, f'{change:+.1f}%', ha='center', va='center', fontsize=14,
                color=color, fontweight='bold', transform=ax.transAxes)
        ax.axis('off')
        ax.set_facecolor('#f8f9fa')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('#dee2e6')

    # Top makes bar chart
    ax = fig.add_subplot(gs[1, :2])
    makes_new = df_new['make'].value_counts().head(8)
    bars = ax.barh(makes_new.index[::-1], makes_new.values[::-1], color=COLORS_PALETTE[:8], edgecolor='black')
    ax.set_xlabel('Number of Listings')
    ax.set_title('Top Makes (December 2025)', fontsize=12, fontweight='bold')
    for bar in bars:
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                f'{int(bar.get_width())}', va='center', fontsize=9)

    # Fuel types bar chart
    ax = fig.add_subplot(gs[1, 2:])
    fuel_new = df_new['fuel_type'].value_counts().head(6)
    bars = ax.barh(fuel_new.index[::-1], fuel_new.values[::-1], color=COLORS_PALETTE[:6], edgecolor='black')
    ax.set_xlabel('Number of Listings')
    ax.set_title('Fuel Types (December 2025)', fontsize=12, fontweight='bold')
    for bar in bars:
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                f'{int(bar.get_width())}', va='center', fontsize=9)

    # Key findings text
    ax = fig.add_subplot(gs[2, :])
    ax.axis('off')

    listings_change = ((stats_new['total_listings'] - stats_old['total_listings']) / stats_old['total_listings']) * 100
    price_change = ((stats_new['avg_price'] - stats_old['avg_price']) / stats_old['avg_price']) * 100
    median_change = ((stats_new['median_price'] - stats_old['median_price']) / stats_old['median_price']) * 100

    findings = f"""
    KEY MARKET FINDINGS (November 2025 → December 2025):

    • Market Size: {stats_new['total_listings']:,} listings ({listings_change:+.1f}% change)
    • Average Price: {stats_new['avg_price']:,.0f} AZN ({price_change:+.1f}% change)
    • Median Price: {stats_new['median_price']:,.0f} AZN ({median_change:+.1f}% change)
    • New Cars: {stats_new['new_cars_pct']:.1f}% of market
    • Credit Available: {stats_new['credit_pct']:.1f}% of listings
    • Barter Available: {stats_new['barter_pct']:.1f}% of listings

    Analysis Period: ~1 month | Data Source: turbo.az
    """

    ax.text(0.5, 0.5, findings, ha='center', va='center', fontsize=12,
            family='monospace', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='#f8f9fa', edgecolor='#dee2e6'))

    plt.savefig(f'{CHARTS_DIR}/16_market_summary.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  Created: 16_market_summary.png")


def generate_insights(stats_old, stats_new, df_old, df_new):
    """Generate key insights and findings"""
    insights = []

    # Listing count change
    listings_change = ((stats_new['total_listings'] - stats_old['total_listings']) / stats_old['total_listings']) * 100
    if listings_change > 0:
        insights.append(f"MARKET GROWTH: Market size increased by {listings_change:.1f}% with {stats_new['total_listings'] - stats_old['total_listings']:,} new listings")
    else:
        insights.append(f"MARKET CONTRACTION: Market size decreased by {abs(listings_change):.1f}% with {abs(stats_new['total_listings'] - stats_old['total_listings']):,} fewer listings")

    # Price changes
    avg_price_change = ((stats_new['avg_price'] - stats_old['avg_price']) / stats_old['avg_price']) * 100
    median_price_change = ((stats_new['median_price'] - stats_old['median_price']) / stats_old['median_price']) * 100

    if avg_price_change > 0:
        insights.append(f"PRICE INFLATION: Average price increased by {avg_price_change:.1f}% (from {stats_old['avg_price']:,.0f} to {stats_new['avg_price']:,.0f} AZN)")
    else:
        insights.append(f"PRICE DEFLATION: Average price decreased by {abs(avg_price_change):.1f}% (from {stats_old['avg_price']:,.0f} to {stats_new['avg_price']:,.0f} AZN)")

    # Top make changes
    makes_old = df_old['make'].value_counts().head(5)
    makes_new = df_new['make'].value_counts().head(5)

    for make in makes_new.head(3).index:
        old_count = makes_old.get(make, 0)
        new_count = makes_new.get(make, 0)
        if old_count > 0:
            change = ((new_count - old_count) / old_count) * 100
            if abs(change) > 5:
                direction = "increased" if change > 0 else "decreased"
                insights.append(f"BRAND TREND: {make} listings {direction} by {abs(change):.1f}%")

    # Fuel type trends
    fuel_old = df_old['fuel_type'].value_counts(normalize=True) * 100
    fuel_new = df_new['fuel_type'].value_counts(normalize=True) * 100

    for fuel in ['Hibrid', 'Elektro', 'Plug-in Hibrid']:
        if fuel in fuel_new.index:
            old_pct = fuel_old.get(fuel, 0)
            new_pct = fuel_new.get(fuel, 0)
            if new_pct - old_pct > 0.5:
                insights.append(f"GREEN TREND: {fuel} vehicles increased from {old_pct:.1f}% to {new_pct:.1f}% market share")

    # Credit availability
    credit_change = stats_new['credit_pct'] - stats_old['credit_pct']
    if abs(credit_change) > 1:
        direction = "increased" if credit_change > 0 else "decreased"
        insights.append(f"FINANCING TREND: Credit availability {direction} by {abs(credit_change):.1f} percentage points")

    return insights


def main():
    """Main execution function"""
    print("="*60)
    print("Turbo.az Market Comparison Analysis")
    print("="*60)

    # File paths
    old_file = 'data/turbo_az_listings_combined_20251123_013059.csv'
    new_file = 'data/turbo_az_listings_20251224_110136.csv'

    # Load data
    print("\n[1/4] Loading data...")
    df_old, df_new = load_and_prepare_data(old_file, new_file)

    # Calculate statistics
    print("\n[2/4] Calculating statistics...")
    stats_old = calculate_statistics(df_old, 'November 2025')
    stats_new = calculate_statistics(df_new, 'December 2025')

    print(f"\n  November 2025 Stats:")
    print(f"    - Total listings: {stats_old['total_listings']:,}")
    print(f"    - Average price: {stats_old['avg_price']:,.0f} AZN")
    print(f"    - Median price: {stats_old['median_price']:,.0f} AZN")

    print(f"\n  December 2025 Stats:")
    print(f"    - Total listings: {stats_new['total_listings']:,}")
    print(f"    - Average price: {stats_new['avg_price']:,.0f} AZN")
    print(f"    - Median price: {stats_new['median_price']:,.0f} AZN")

    # Generate charts
    print("\n[3/4] Generating charts...")
    chart_01_market_overview(df_old, df_new, stats_old, stats_new)
    chart_02_price_distribution(df_old, df_new)
    chart_03_top_makes_comparison(df_old, df_new)
    chart_04_avg_price_by_make(df_old, df_new)
    chart_05_fuel_type_trends(df_old, df_new)
    chart_06_transmission_trends(df_old, df_new)
    chart_07_body_type_analysis(df_old, df_new)
    chart_08_year_distribution(df_old, df_new)
    chart_09_city_distribution(df_old, df_new)
    chart_10_price_segments(df_old, df_new)
    chart_11_listing_features(df_old, df_new)
    chart_12_mileage_vs_price(df_old, df_new)
    chart_13_color_trends(df_old, df_new)
    chart_14_new_vs_used(df_old, df_new)
    chart_15_top_models(df_old, df_new)
    chart_16_market_summary(stats_old, stats_new, df_old, df_new)

    # Generate insights
    print("\n[4/4] Generating insights...")
    insights = generate_insights(stats_old, stats_new, df_old, df_new)

    print("\n" + "="*60)
    print("KEY MARKET INSIGHTS")
    print("="*60)
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight}")

    print("\n" + "="*60)
    print(f"Analysis complete! {16} charts saved to '{CHARTS_DIR}/' folder")
    print("="*60)

    return stats_old, stats_new, insights


if __name__ == "__main__":
    main()
