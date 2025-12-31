import { NextResponse } from "next/server"
import { Pool } from "pg"

// Force dynamic rendering - no caching
export const dynamic = 'force-dynamic'
export const revalidate = 0

// Azerbaijan CPI data (November 2025 baseline = 233.40)
// Source: State Statistical Committee of Azerbaijan
const CPI_DATA: { [key: string]: number } = {
  "2025-11": 233.40,
  "2025-10": 232.70, // Previous month
  "2024-12": 230.0,  // Estimated historical (scaled proportionally)
  "2024-11": 229.0,
  "2024-10": 228.0,
  "2024-09": 227.0,
  "2024-08": 226.5,
  "2024-07": 226.0,
  "2024-06": 225.5,
  "2024-05": 225.0,
  "2024-04": 224.5,
  "2024-03": 224.0,
  "2024-02": 223.5,
  "2024-01": 223.0,
}

export async function GET() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  })

  try {
    // Monthly price trends with aggregations
    const monthlyTrends = await pool.query(`
      SELECT
        DATE_TRUNC('month', scraped_at) as month,
        COUNT(*) as listing_volume,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as median_price,
        AVG(CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as avg_price,
        PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as p10_price,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as p90_price,
        STDDEV(CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as price_volatility
      FROM scraping.turbo_az
      WHERE price_azn IS NOT NULL
        AND price_azn != ''
        AND scraped_at >= NOW() - INTERVAL '12 months'
      GROUP BY DATE_TRUNC('month', scraped_at)
      ORDER BY month
    `)

    // Price by vehicle age (depreciation analysis)
    const priceByAge = await pool.query(`
      SELECT
        CASE
          WHEN 2025 - year <= 3 THEN '0-3 years'
          WHEN 2025 - year <= 7 THEN '4-7 years'
          WHEN 2025 - year <= 12 THEN '8-12 years'
          ELSE '13+ years'
        END as age_bucket,
        COUNT(*) as count,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as median_price,
        AVG(CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as avg_price
      FROM scraping.turbo_az
      WHERE price_azn IS NOT NULL
        AND price_azn != ''
        AND year IS NOT NULL
        AND year >= 2000
      GROUP BY age_bucket
      ORDER BY age_bucket
    `)

    // Price trends by top segments
    const segmentTrends = await pool.query(`
      SELECT
        body_type,
        DATE_TRUNC('month', scraped_at) as month,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as median_price,
        COUNT(*) as volume
      FROM scraping.turbo_az
      WHERE price_azn IS NOT NULL
        AND price_azn != ''
        AND body_type IS NOT NULL
        AND scraped_at >= NOW() - INTERVAL '12 months'
      GROUP BY body_type, DATE_TRUNC('month', scraped_at)
      HAVING COUNT(*) >= 10
      ORDER BY body_type, month
    `)

    // Price vs mileage correlation
    const priceVsMileage = await pool.query(`
      SELECT
        CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER) as price,
        CAST(REGEXP_REPLACE(SPLIT_PART(mileage, ' ', 1), '[^0-9]', '', 'g') AS INTEGER) as mileage_km,
        2025 - year as vehicle_age,
        make
      FROM scraping.turbo_az
      WHERE price_azn IS NOT NULL
        AND price_azn != ''
        AND mileage IS NOT NULL
        AND year IS NOT NULL
        AND year >= 2010
        AND CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER) BETWEEN 5000 AND 200000
        AND CAST(REGEXP_REPLACE(SPLIT_PART(mileage, ' ', 1), '[^0-9]', '', 'g') AS INTEGER) < 500000
      ORDER BY RANDOM()
      LIMIT 500
    `)

    // Calculate inflation-adjusted prices
    const trendsWithInflation = monthlyTrends.rows.map((row: any) => {
      const monthKey = new Date(row.month).toISOString().substring(0, 7)
      const cpiIndex = CPI_DATA[monthKey] || 233.40
      const cpiBase = 233.40 // November 2025 baseline

      return {
        month: row.month,
        listing_volume: parseInt(row.listing_volume),
        median_price_nominal: Math.round(parseFloat(row.median_price)),
        median_price_real: Math.round((parseFloat(row.median_price) / cpiIndex) * cpiBase),
        avg_price: Math.round(parseFloat(row.avg_price)),
        p10_price: Math.round(parseFloat(row.p10_price)),
        p90_price: Math.round(parseFloat(row.p90_price)),
        price_volatility: Math.round(parseFloat(row.price_volatility || 0)),
        cpi_index: cpiIndex,
      }
    })

    // Calculate month-over-month changes
    const latestMonth = trendsWithInflation[trendsWithInflation.length - 1]
    const previousMonth = trendsWithInflation[trendsWithInflation.length - 2]
    const yearAgo = trendsWithInflation[Math.max(0, trendsWithInflation.length - 13)]

    const momChange = previousMonth
      ? ((latestMonth.median_price_nominal - previousMonth.median_price_nominal) / previousMonth.median_price_nominal) * 100
      : 0

    const yoyChange = yearAgo
      ? ((latestMonth.median_price_nominal - yearAgo.median_price_nominal) / yearAgo.median_price_nominal) * 100
      : 0

    // Executive summary metrics
    const executiveSummary = {
      current_median_price: latestMonth.median_price_nominal,
      current_median_price_real: latestMonth.median_price_real,
      mom_change_percent: momChange.toFixed(1),
      yoy_change_percent: yoyChange.toFixed(1),
      current_volume: latestMonth.listing_volume,
      volume_trend: previousMonth
        ? ((latestMonth.listing_volume - previousMonth.listing_volume) / previousMonth.listing_volume) * 100
        : 0,
      price_volatility: latestMonth.price_volatility,
      data_coverage_months: trendsWithInflation.length,
    }

    await pool.end()

    return NextResponse.json({
      executiveSummary,
      monthlyTrends: trendsWithInflation,
      priceByAge: priceByAge.rows.map((row: any) => ({
        age_bucket: row.age_bucket,
        count: parseInt(row.count),
        median_price: Math.round(parseFloat(row.median_price)),
        avg_price: Math.round(parseFloat(row.avg_price)),
      })),
      segmentTrends: segmentTrends.rows.map((row: any) => ({
        body_type: row.body_type,
        month: row.month,
        median_price: Math.round(parseFloat(row.median_price)),
        volume: parseInt(row.volume),
      })),
      priceVsMileage: priceVsMileage.rows,
      cpiData: CPI_DATA,
    })
  } catch (error: any) {
    await pool.end()
    console.error("Trends API Error:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch trends data" },
      { status: 500 }
    )
  }
}
