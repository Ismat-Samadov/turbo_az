# TURBO.AZ CAR MARKET ANALYTICS - EXECUTIVE ANALYSIS PROMPT

## PURPOSE
Produce a business-focused analysis and executive-ready dashboard showing how car prices have changed over time in Azerbaijan's automotive market, explain driving factors (including inflation), and highlight market dynamics and risks. Prioritize clarity for business stakeholders: present concise executive summary bullets, clear charts, and prioritized recommendations.

---

## INPUT DATA (PostgreSQL Database)

**Primary Dataset:** `scraping.turbo_az` table in PostgreSQL database

### Available Columns:
```sql
- listing_id (integer, primary key): Unique identifier
- listing_url (text): Source URL
- title (text): Car listing title
- price_azn (text): Price in Azerbaijan Manat (format: "50 000 AZN")
- make (text): Car manufacturer (Mercedes, BMW, Toyota, etc.)
- model (text): Car model name
- year (integer): Manufacturing year (1980-2026)
- mileage (text): Odometer reading (format: "150 000 km")
- engine_volume (text): Engine displacement (e.g., "2.0")
- engine_power (text): Engine power in HP
- fuel_type (text): Benzin, Dizel, Elektro, Hibrid, Plug-in Hibrid
- transmission (text): Avtom at(AT/Variator/Robot), Mexaniki(MT)
- drivetrain (text): Ön, Arxa, Tam (Front/Rear/AWD)
- body_type (text): Sedan, Offroader, Hetçbek, Kupe, Minivan, etc.
- color (text): Vehicle color
- seats_count (integer): Number of seats
- condition (text): Sürülmüş, Qəzalı, Yeni (Used, Damaged, New)
- market (text): Market origin
- is_new (text): New or used indicator
- city (text): Location (Bakı, Sumqayıt, Gəncə, etc.)
- seller_name (text): Seller name
- seller_phone (jsonb): Phone numbers array
- description (text): Listing description
- extras (text): Additional features
- views (integer): Number of views
- updated_date (text): Last update date
- posted_date (text): Initial post date
- is_vip (boolean): VIP listing flag
- is_featured (boolean): Featured listing flag
- is_salon (boolean): Salon (dealer) listing flag
- has_credit (boolean): Credit available
- has_barter (boolean): Barter available
- has_vin (boolean): VIN code available
- image_urls (text): Image URLs
- scraped_at (timestamp): Data collection timestamp
```

### Auxiliary Data:
- **CPI Data**: Azerbaijan Consumer Price Index (2024 baseline = 100)
- **Currency**: Azerbaijan Manat (AZN)
- **Market**: Azerbaijan automotive market
- **Geography**: Primary cities - Bakı, Sumqayıt, Gəncə, Mingəçevir

---

## PREPROCESSING REQUIREMENTS

### 1. Price Normalization
```sql
-- Convert price_azn text to numeric
CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER) as price_numeric

-- Remove outliers (prices outside 1,000-500,000 AZN range)
WHERE price_numeric BETWEEN 1000 AND 500000
```

### 2. Mileage Normalization
```sql
-- Extract numeric mileage from text
CAST(REGEXP_REPLACE(SPLIT_PART(mileage, ' ', 1), '[^0-9]', '', 'g') AS INTEGER) as mileage_km

-- Flag unrealistic values (> 1,000,000 km)
WHERE mileage_km < 1000000
```

### 3. Derived Variables
```sql
-- Vehicle age
vehicle_age = 2025 - year

-- Age buckets for depreciation analysis
CASE
  WHEN 2025 - year <= 3 THEN '0-3 years'
  WHEN 2025 - year <= 7 THEN '4-7 years'
  WHEN 2025 - year <= 12 THEN '8-12 years'
  ELSE '13+ years'
END as age_bucket

-- Price per kilometer
price_per_km = price_numeric / NULLIF(mileage_km, 0)

-- Transmission normalization
CASE
  WHEN transmission ILIKE '%avtomat%' THEN 'Automatic'
  WHEN transmission ILIKE '%mexaniki%' THEN 'Manual'
  ELSE transmission
END as transmission_normalized

-- Popular brand flag (top 10 by volume)
is_popular_brand = make IN (SELECT make FROM top_10_makes)
```

### 4. Time Bucketing
```sql
-- Monthly aggregation (primary)
DATE_TRUNC('month', scraped_at) as month

-- Weekly for short-term dynamics
DATE_TRUNC('week', scraped_at) as week
```

---

## INFLATION ADJUSTMENT (Azerbaijan CPI)

### Real Price Calculation
```
real_price = (nominal_price / CPI_index) * CPI_base
```
Where:
- `CPI_base` = 100 (December 2024 baseline)
- `CPI_index` = Monthly CPI value from State Statistical Committee

### Required Analyses
1. **Nominal vs Real Price Charts**: Show both time series
2. **Inflation Elasticity**: `log(median_price) ~ log(CPI)`
3. **Correlation Analysis**: Month-over-month price vs CPI changes

---

## KEY METRICS TO CALCULATE (Monthly Rollups)

### Volume Metrics
- `listing_volume`: COUNT of new listings per month
- `new_vs_used_ratio`: Percentage of new vs used vehicles
- `dealer_vs_private_ratio`: Salon vs private seller distribution

### Price Metrics
```sql
-- Central tendency
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price
AVG(price) as mean_price

-- Distribution
PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY price) as p10_price
PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY price) as p90_price
PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price) as q1_price
PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price) as q3_price

-- Volatility
STDDEV(price) as price_volatility
```

### Segment Metrics
- Median price by: `body_type`, `make`, `age_bucket`, `fuel_type`, `transmission`, `city`
- Volume distribution by segment
- Market share by segment

### Change Metrics
- Month-over-Month (MoM): `(current_month - prev_month) / prev_month * 100`
- Year-over-Year (YoY): `(current_month - year_ago_month) / year_ago_month * 100`
- Rolling 3-month average
- Rolling 12-month volatility

---

## REQUIRED CHARTS (Business-Appropriate)

### 1. Executive Time-Series Panel
**Chart Type**: Dual-axis line chart
- **Primary Y-axis**: Median price (AZN) - two lines:
  - Nominal price (solid line)
  - Inflation-adjusted real price (dashed line)
- **Secondary Y-axis**: Listing volume (bar chart, semi-transparent)
- **X-axis**: Time (monthly)
- **Confidence band**: 10th-90th percentile shaded area

### 2. Price Volatility Tracker
**Chart Type**: Line chart with area fill
- Rolling 3-month and 12-month price standard deviation
- Highlight high-volatility periods

### 3. Depreciation Heatmap
**Chart Type**: Heatmap
- **Rows**: Vehicle age buckets (0-3y, 4-7y, 8-12y, 13+y)
- **Columns**: Months
- **Values**: Median price (color intensity)

### 4. Segment Dynamics
**Chart Type**: Small multiples (faceted line charts)
- One panel per body_type (Sedan, SUV/Offroader, Hetçbek, etc.)
- Show median price trends over time
- Include volume as secondary indicator

### 5. Geographic Price Distribution
**Chart Type**: Horizontal bar chart (sorted)
- **Y-axis**: Cities (Bakı, Sumqayıt, Gəncə, etc.)
- **X-axis**: Median price
- **Color**: % change vs previous quarter

### 6. Top Brands Price Evolution
**Chart Type**: Multi-line chart
- Top 10 makes by volume
- Monthly median price trends
- Interactive legend to toggle brands

### 7. Price vs Mileage Correlation
**Chart Type**: Scatter plot with regression
- **X-axis**: Mileage (km)
- **Y-axis**: Price (AZN)
- **Color**: Age bucket
- **Fit line**: LOWESS regression
- **Transparency**: Points with alpha = 0.3

### 8. Market Concentration Analysis
**Chart Type**: Stacked area chart
- Market share over time for top 5 brands
- "Others" category for remaining brands

### 9. Fuel Type Transition
**Chart Type**: Stacked bar chart (100%)
- Monthly distribution: Benzin, Dizel, Hybrid, Electric
- Show transition to electric/hybrid vehicles

### 10. Price Elasticity Visualization
**Chart Type**: Scatter plot with regression line
- **X-axis**: CPI index
- **Y-axis**: Median nominal price
- **Annotation**: Elasticity coefficient and R²

---

## STATISTICAL ANALYSES (Business-Readable)

### 1. Trend Analysis
**Method**: Mann-Kendall trend test
**Output**: "Median prices show statistically significant upward trend (p < 0.05, tau = 0.67)"

### 2. Seasonality Detection
**Method**: Seasonal decomposition (STL)
**Output**:
- Seasonal index by month (multiplier)
- "Peak listing volume occurs in March-April (+15% above average)"

### 3. Inflation Elasticity
**Method**: Log-log regression
```
log(median_price) = β₀ + β₁ * log(CPI) + ε
```
**Output**: "1% CPI increase → 0.15% price increase (95% CI: 0.10-0.20)"

### 4. Depreciation Rate
**Method**: Exponential regression by age
```
price = initial_price * e^(-depreciation_rate * age)
```
**Output**: "Average annual depreciation: 12.3%"

### 5. Market Efficiency
**Method**: Granger causality test
**Output**: "CPI Granger-causes car prices with 2-month lag (F-stat = 8.4, p = 0.002)"

---

## DASHBOARD LAYOUT (Executive-First Design)

### Row 1: Executive Summary Card
```
┌─────────────────────────────────────────────────────────┐
│ EXECUTIVE SUMMARY - Car Market Dynamics                │
├─────────────────────────────────────────────────────────┤
│ • Current Median Price: 35,420 AZN (+3.2% MoM, +8.5% YoY│
│ • Real Price (inflation-adj): 34,180 AZN (+1.8% YoY)    │
│ • Market Activity: 13,853 listings (+5.2% vs last month)│
│                                                          │
│ Key Insight: Real prices stabilizing after 12-month     │
│ surge; SUV segment shows strongest demand pressure      │
└─────────────────────────────────────────────────────────┘
```

### Row 2: Primary Trends
- Left: Median Price (Nominal vs Real) + Volume
- Right: Price Volatility + Seasonality Index

### Row 3: Market Segmentation
- Left: Body Type Price Trends (small multiples)
- Right: Geographic Distribution (bar chart)

### Row 4: Deep Dive
- Left: Depreciation Heatmap
- Right: Top Brands Evolution

### Row 5: Correlations & Drivers
- Left: Price vs Mileage (scatter)
- Right: CPI Elasticity (scatter with regression)

### Row 6: Forward-Looking
- Forecast chart (12-month projection with confidence intervals)
- Scenario analysis (base, high-inflation, recession)

---

## INSIGHTS & NARRATIVE STRUCTURE

### For Each Chart, Provide:

1. **Headline Insight** (one sentence)
   - Example: "Real median used-car prices rose 6.3% YoY despite inflation adjustment"

2. **Supporting Facts** (2 bullet points with numbers)
   - "Nominal prices increased from 32,500 AZN to 35,420 AZN (Jan-Dec 2024)"
   - "CPI-adjusted prices show 4.8% real increase vs 8.5% nominal"

3. **Business Implication** (1-2 sentences)
   - "Persistent real price growth indicates strong demand fundamentals beyond inflation; consider tightening loan-to-value ratios for vehicles >8 years old"

4. **Risk Factor** (1 sentence)
   - "Price stability depends on continued manat exchange rate stability and oil revenue flow"

5. **Recommended Action** (specific, actionable)
   - "Monitor SUV segment closely—12% YoY price increase suggests inventory shortages; prioritize dealer partnerships for high-demand models"

---

## CEO-FACING INSIGHT EXAMPLES (Azerbaijan Context)

✓ **Price Dynamics**
- "After adjusting for Azerbaijan CPI (base Dec 2024), median nominal price increased 18% over 12 months; real increase is 10.2%—indicating strong underlying demand"

✓ **Segment Performance**
- "SUV/Offroader segment commands 35% premium over sedans; demand grew 8% YoY while supply decreased 5%, creating seller's market conditions"

✓ **Geographic Concentration**
- "Bakı accounts for 79% of listings; average prices in Sumqayıt are 12% lower—regional expansion opportunity exists"

✓ **Technology Shift**
- "Hybrid and electric listings increased from 8% to 14% of market share in 12 months; median hybrid price (45,000 AZN) stable despite rising demand"

✓ **Depreciation Insights**
- "Vehicles aged 4-7 years show steepest depreciation curve (-18% annually); newer vehicles (<3y) retain 92% of original value"

✓ **Inflation Impact**
- "Estimated price elasticity: 0.15 (p<0.01)—indicating car prices are moderately sensitive to CPI but not perfectly correlated; other demand factors dominate"

✓ **Market Forecast**
- "Base case scenario: real median prices expected to stabilize at 36,000-38,000 AZN over next 6 months; downside risk (economic slowdown) could trigger 5-8% correction"

---

## DELIVERABLES CHECKLIST

- [ ] **Executive 1-page PDF**: Summary + key charts
- [ ] **5-slide deck**: For stakeholder presentation
- [ ] **Interactive dashboard**: Filters (time, city, brand, segment)
- [ ] **CSV exports**:
  - `monthly_aggregates.csv` (all metrics by month)
  - `segment_analysis.csv` (by body_type, make, age_bucket)
  - `forecast_data.csv` (12-month projections)
- [ ] **Appendix notebook**: Methodology and reproducible analysis

---

## TECHNICAL NOTES (Appendix Only)

### Data Quality
- **Coverage**: Full market scraping from Turbo.az
- **Sample Size**: 13,853 current listings
- **Time Period**: Last 12 months of historical data
- **Missing Data**: <2% for price, <5% for mileage
- **Outliers Removed**: 147 listings (extreme prices or mileage)

### Assumptions
- CPI data from Azerbaijan State Statistical Committee
- Currency: All prices in AZN (no conversion needed)
- Inflation baseline: December 2024 = 100
- Depreciation modeled as exponential decay
- Forecast uncertainty: ±5% at 95% confidence

### Methodology
- Aggregation: Monthly (primary), Weekly (secondary)
- Outlier detection: IQR method (1.5× rule)
- Missing value handling: Median imputation for mileage (<3% affected)
- Statistical significance threshold: α = 0.05

---

## USAGE INSTRUCTIONS

Replace these placeholders in implementation:
- `{DATABASE_URL}`: PostgreSQL connection string
- `{CPI_FILE}`: Path to CPI time series (or use embedded data)
- `{REPORT_DATE}`: Current analysis date
- `{OUTPUT_DIR}`: Directory for deliverables

---

**End of Analytics Prompt**
*Adapted for Turbo.az Azerbaijan Car Market - Version 1.0*
