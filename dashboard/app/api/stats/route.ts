import { NextResponse } from "next/server"
import { Pool } from "pg"

// Force dynamic rendering - no caching, no static generation
export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function GET() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  })

  try {
    // Run all stats queries in parallel
    const [
      totalResult,
      byMakeResult,
      byCityResult,
      byFuelTypeResult,
      byYearResult,
      byTransmissionResult,
      byBodyTypeResult,
      avgPriceByMakeResult,
      conditionResult,
    ] = await Promise.all([
      pool.query("SELECT COUNT(*) as total FROM scraping.turbo_az"),
      pool.query("SELECT make, COUNT(*) as count FROM scraping.turbo_az WHERE make IS NOT NULL GROUP BY make ORDER BY count DESC LIMIT 8"),
      pool.query("SELECT city, COUNT(*) as count FROM scraping.turbo_az WHERE city IS NOT NULL GROUP BY city ORDER BY count DESC LIMIT 6"),
      pool.query("SELECT fuel_type, COUNT(*) as count FROM scraping.turbo_az WHERE fuel_type IS NOT NULL GROUP BY fuel_type ORDER BY count DESC LIMIT 5"),
      pool.query("SELECT year, COUNT(*) as count FROM scraping.turbo_az WHERE year IS NOT NULL AND year >= 2015 GROUP BY year ORDER BY year DESC LIMIT 10"),
      pool.query(`
        SELECT
          CASE
            WHEN transmission ILIKE '%avtomat%' OR transmission ILIKE '%automatic%' THEN 'Automatic'
            WHEN transmission ILIKE '%mexaniki%' OR transmission ILIKE '%manual%' THEN 'Manual'
            ELSE transmission
          END as transmission,
          COUNT(*) as count
        FROM scraping.turbo_az
        WHERE transmission IS NOT NULL
        GROUP BY
          CASE
            WHEN transmission ILIKE '%avtomat%' OR transmission ILIKE '%automatic%' THEN 'Automatic'
            WHEN transmission ILIKE '%mexaniki%' OR transmission ILIKE '%manual%' THEN 'Manual'
            ELSE transmission
          END
        ORDER BY count DESC
      `),
      pool.query("SELECT body_type, COUNT(*) as count FROM scraping.turbo_az WHERE body_type IS NOT NULL GROUP BY body_type ORDER BY count DESC LIMIT 6"),
      pool.query(`
        SELECT
          make,
          COUNT(*) as count,
          AVG(CAST(REGEXP_REPLACE(price_azn, '[^0-9]', '', 'g') AS INTEGER)) as avg_price
        FROM scraping.turbo_az
        WHERE make IS NOT NULL
          AND price_azn IS NOT NULL
          AND price_azn != ''
        GROUP BY make
        HAVING COUNT(*) >= 100
        ORDER BY count DESC
        LIMIT 10
      `),
      pool.query("SELECT condition, COUNT(*) as count FROM scraping.turbo_az WHERE condition IS NOT NULL GROUP BY condition ORDER BY count DESC"),
    ])

    // Get last scrape time from database
    const lastScrapeResult = await pool.query(
      "SELECT MAX(scraped_at) as last_scrape FROM scraping.turbo_az"
    )

    await pool.end()

    return NextResponse.json({
      total: parseInt(totalResult.rows[0]?.total || "0"),
      lastScraped: lastScrapeResult.rows[0]?.last_scrape || null,
      byMake: byMakeResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      byCity: byCityResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      byFuelType: byFuelTypeResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      byYear: byYearResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      byTransmission: byTransmissionResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      byBodyType: byBodyTypeResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
      avgPriceByMake: avgPriceByMakeResult.rows.map(row => ({
        make: row.make,
        count: parseInt(row.count),
        avg_price: Math.round(parseFloat(row.avg_price))
      })),
      byCondition: conditionResult.rows.map(row => ({
        ...row,
        count: parseInt(row.count)
      })),
    })
  } catch (error: any) {
    await pool.end()
    console.error("Stats API Error:", error)
    return NextResponse.json(
      { error: error.message || "Failed to fetch stats" },
      { status: 500 }
    )
  }
}
