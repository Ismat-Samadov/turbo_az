import { NextResponse } from "next/server"
import { Pool } from "pg"

export async function GET() {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  })

  try {
    // Run all stats queries in parallel
    const [totalResult, byMakeResult, byCityResult, byFuelTypeResult] = await Promise.all([
      pool.query("SELECT COUNT(*) as total FROM scraping.turbo_az"),
      pool.query("SELECT make, COUNT(*) as count FROM scraping.turbo_az WHERE make IS NOT NULL GROUP BY make ORDER BY count DESC LIMIT 8"),
      pool.query("SELECT city, COUNT(*) as count FROM scraping.turbo_az WHERE city IS NOT NULL GROUP BY city ORDER BY count DESC LIMIT 6"),
      pool.query("SELECT fuel_type, COUNT(*) as count FROM scraping.turbo_az WHERE fuel_type IS NOT NULL GROUP BY fuel_type ORDER BY count DESC LIMIT 5"),
    ])

    await pool.end()

    return NextResponse.json({
      total: parseInt(totalResult.rows[0]?.total || "0"),
      byMake: byMakeResult.rows,
      byCity: byCityResult.rows,
      byFuelType: byFuelTypeResult.rows,
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
