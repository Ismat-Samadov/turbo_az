"""
BrightData Proxy Expense Analysis
Analyzes scraping costs and provides projections
"""
import pandas as pd
from datetime import datetime

print("="*80)
print("BRIGHTDATA PROXY EXPENSE ANALYSIS")
print("="*80)

# ============================================================================
# ACTUAL DATA FROM SCRAPING RUN (31-Dec-2025)
# ============================================================================

print("\n📊 SCRAPING RUN SUMMARY (10 pages test)")
print("-"*80)

# Balance & Cost
balance_before = 1.06  # USD
balance_after = 0.97   # USD
total_spent = balance_before - balance_after

print(f"Balance Before:  ${balance_before:.2f}")
print(f"Balance After:   ${balance_after:.2f}")
print(f"Total Spent:     ${total_spent:.3f}")

# BrightData Metrics
bandwidth_used = 11.5  # MB
total_requests = 447

print(f"\nBandwidth Used:  {bandwidth_used} MB")
print(f"Total Requests:  {total_requests:,}")

# Scraping Results
pages_scraped = 10
listings_scraped = 216
time_taken = 1449.10  # seconds
avg_time_per_listing = 6.71  # seconds

print(f"\nPages Scraped:   {pages_scraped}")
print(f"Listings Found:  {listings_scraped}")
print(f"Time Taken:      {time_taken:.0f}s ({time_taken/60:.1f} minutes)")
print(f"Avg per Listing: {avg_time_per_listing:.2f}s")

# ============================================================================
# REQUEST BREAKDOWN ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("🔍 REQUEST BREAKDOWN ANALYSIS")
print("="*80)

# Calculate expected requests
page_requests = pages_scraped
listing_detail_requests = listings_scraped
phone_requests = listings_scraped  # AJAX call for each listing

expected_requests = page_requests + listing_detail_requests + phone_requests
extra_requests = total_requests - expected_requests

print(f"\nPage Fetches:           {page_requests:4} requests")
print(f"Listing Detail Fetches: {listing_detail_requests:4} requests")
print(f"Phone Number Fetches:   {phone_requests:4} requests (AJAX)")
print("-" * 40)
print(f"Expected Total:         {expected_requests:4} requests")
print(f"Actual Total:           {total_requests:4} requests")
print(f"Extra/Retry Requests:   {extra_requests:4} requests ({extra_requests/total_requests*100:.1f}%)")

# ============================================================================
# COST ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("💰 COST ANALYSIS")
print("="*80)

cost_per_request = total_spent / total_requests if total_requests > 0 else 0
cost_per_1k_requests = cost_per_request * 1000
cost_per_mb = total_spent / bandwidth_used if bandwidth_used > 0 else 0
cost_per_listing = total_spent / listings_scraped if listings_scraped > 0 else 0
cost_per_page = total_spent / pages_scraped if pages_scraped > 0 else 0

print(f"\nCost per Request:        ${cost_per_request:.6f}")
print(f"Cost per 1K Requests:    ${cost_per_1k_requests:.4f}")
print(f"Cost per MB:             ${cost_per_mb:.6f}")
print(f"Cost per Listing:        ${cost_per_listing:.6f}")
print(f"Cost per Page:           ${cost_per_page:.5f}")

# ============================================================================
# EFFICIENCY METRICS
# ============================================================================

print("\n" + "="*80)
print("⚡ EFFICIENCY METRICS")
print("="*80)

listings_per_page = listings_scraped / pages_scraped
requests_per_listing = total_requests / listings_scraped
bandwidth_per_listing = bandwidth_used / listings_scraped
bandwidth_per_request = bandwidth_used / total_requests

print(f"\nListings per Page:       {listings_per_page:.1f} listings/page")
print(f"Requests per Listing:    {requests_per_listing:.1f} requests/listing")
print(f"Bandwidth per Listing:   {bandwidth_per_listing:.3f} MB/listing")
print(f"Bandwidth per Request:   {bandwidth_per_request:.3f} MB/request")

# ============================================================================
# FULL SCRAPE PROJECTIONS
# ============================================================================

print("\n" + "="*80)
print("📈 FULL SCRAPE PROJECTIONS")
print("="*80)

# Configuration from .env (typical full scrape)
total_pages_full = 1770

# Projections
estimated_listings = int(listings_per_page * total_pages_full)
estimated_page_requests = total_pages_full
estimated_listing_requests = estimated_listings
estimated_phone_requests = estimated_listings
estimated_total_requests = estimated_page_requests + estimated_listing_requests + estimated_phone_requests
estimated_bandwidth = bandwidth_per_request * estimated_total_requests
estimated_cost = cost_per_request * estimated_total_requests
estimated_time_seconds = avg_time_per_listing * estimated_listings
estimated_time_hours = estimated_time_seconds / 3600

print(f"\n📋 Full Scrape Estimates (1-{total_pages_full} pages):")
print("-"*80)
print(f"Expected Listings:       {estimated_listings:,}")
print(f"Expected Requests:       {estimated_total_requests:,}")
print(f"  - Page fetches:        {estimated_page_requests:,}")
print(f"  - Listing details:     {estimated_listing_requests:,}")
print(f"  - Phone numbers:       {estimated_phone_requests:,}")
print(f"\nExpected Bandwidth:      {estimated_bandwidth:,.1f} MB ({estimated_bandwidth/1024:.2f} GB)")
print(f"Expected Cost:           ${estimated_cost:.2f}")
print(f"Expected Time:           {estimated_time_hours:.1f} hours ({estimated_time_hours/24:.1f} days)")

# ============================================================================
# BUDGET SCENARIOS
# ============================================================================

print("\n" + "="*80)
print("💵 BUDGET SCENARIOS")
print("="*80)

budgets = [1.00, 5.00, 10.00, 20.00, 50.00, 100.00]

print("\nWhat you can scrape with different budgets:")
print("-"*80)
print(f"{'Budget':<12} {'Pages':<10} {'Listings':<12} {'Requests':<12} {'Bandwidth':<12}")
print("-"*80)

for budget in budgets:
    max_requests = int(budget / cost_per_request)
    # Each page cycle = 1 page req + ~21.6 listings + ~21.6 phone reqs = ~44.2 requests
    requests_per_page_cycle = 1 + listings_per_page + listings_per_page
    max_pages = int(max_requests / requests_per_page_cycle)
    max_listings = int(max_pages * listings_per_page)
    max_bandwidth = max_requests * bandwidth_per_request

    print(f"${budget:<11.2f} {max_pages:<10,} {max_listings:<12,} {max_requests:<12,} {max_bandwidth:<11.1f} MB")

# ============================================================================
# COST BREAKDOWN BY OPERATION
# ============================================================================

print("\n" + "="*80)
print("📑 COST BREAKDOWN BY OPERATION TYPE")
print("="*80)

cost_page_fetches = page_requests * cost_per_request
cost_listing_details = listing_detail_requests * cost_per_request
cost_phone_fetches = phone_requests * cost_per_request

print(f"\nPage Fetches:            ${cost_page_fetches:.5f} ({cost_page_fetches/total_spent*100:.1f}%)")
print(f"Listing Details:         ${cost_listing_details:.5f} ({cost_listing_details/total_spent*100:.1f}%)")
print(f"Phone Number AJAX:       ${cost_phone_fetches:.5f} ({cost_phone_fetches/total_spent*100:.1f}%)")
print("-" * 40)
print(f"Total:                   ${total_spent:.5f}")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("\n" + "="*80)
print("💡 RECOMMENDATIONS")
print("="*80)

# Calculate if phone fetching is worth it
phone_cost_percentage = (phone_requests / total_requests) * 100
phone_savings = phone_requests * cost_per_request

print(f"\n1. Phone Number Fetching:")
print(f"   • Accounts for {phone_cost_percentage:.1f}% of requests")
print(f"   • Costs ${phone_cost_percentage/100*estimated_cost:.2f} for full scrape")
print(f"   • Disabling would save ~${phone_savings:.3f} per {listings_scraped} listings")
print(f"   • Recommendation: {'Keep enabled - valuable data' if phone_cost_percentage < 40 else 'Consider disabling if budget is tight'}")

print(f"\n2. Full Scrape Budget:")
print(f"   • Estimated cost: ${estimated_cost:.2f}")
print(f"   • Current balance: ${balance_after:.2f}")
print(f"   • Additional funds needed: ${max(0, estimated_cost - balance_after):.2f}")

print(f"\n3. Optimization Opportunities:")
pages_with_current_balance = int(balance_after / cost_per_page)
listings_with_current_balance = int(pages_with_current_balance * listings_per_page)
print(f"   • With current ${balance_after:.2f} balance, you can scrape:")
print(f"     - ~{pages_with_current_balance} pages")
print(f"     - ~{listings_with_current_balance:,} listings")
print(f"   • Consider scraping in batches to manage costs")

print(f"\n4. Cost Efficiency:")
print(f"   • Current rate: ${cost_per_1k_requests:.4f} per 1K requests")
print(f"   • This is {'reasonable' if cost_per_1k_requests < 0.30 else 'high'} for residential proxies")
print(f"   • You're getting {listings_per_page:.1f} listings per page (good density)")

# ============================================================================
# EXPORT TO CSV
# ============================================================================

print("\n" + "="*80)
print("💾 SAVING ANALYSIS")
print("="*80)

# Create detailed breakdown
analysis_data = {
    'Metric': [
        'Balance Before (USD)',
        'Balance After (USD)',
        'Total Spent (USD)',
        'Bandwidth Used (MB)',
        'Total Requests',
        'Pages Scraped',
        'Listings Scraped',
        'Time Taken (seconds)',
        'Avg Time per Listing (s)',
        'Cost per Request (USD)',
        'Cost per 1K Requests (USD)',
        'Cost per MB (USD)',
        'Cost per Listing (USD)',
        'Cost per Page (USD)',
        'Listings per Page',
        'Requests per Listing',
        'Bandwidth per Listing (MB)',
        'Bandwidth per Request (MB)',
        'Estimated Full Scrape Listings',
        'Estimated Full Scrape Requests',
        'Estimated Full Scrape Bandwidth (MB)',
        'Estimated Full Scrape Cost (USD)',
        'Estimated Full Scrape Time (hours)',
    ],
    'Value': [
        balance_before,
        balance_after,
        total_spent,
        bandwidth_used,
        total_requests,
        pages_scraped,
        listings_scraped,
        time_taken,
        avg_time_per_listing,
        cost_per_request,
        cost_per_1k_requests,
        cost_per_mb,
        cost_per_listing,
        cost_per_page,
        listings_per_page,
        requests_per_listing,
        bandwidth_per_listing,
        bandwidth_per_request,
        estimated_listings,
        estimated_total_requests,
        estimated_bandwidth,
        estimated_cost,
        estimated_time_hours,
    ]
}

df = pd.DataFrame(analysis_data)
output_file = f"../data/expense_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ Analysis saved to: {output_file}")
print("\n" + "="*80)
