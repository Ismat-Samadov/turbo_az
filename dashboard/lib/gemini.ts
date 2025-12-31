import { GoogleGenerativeAI } from "@google/generative-ai"
import { Pool } from "pg"

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!)

// Database schema documentation for Gemini
const DATABASE_SCHEMA = `
You are an AI assistant with access to a PostgreSQL database containing Turbo.az car listings.

DATABASE SCHEMA:
Table: scraping.turbo_az

Columns:
- listing_id (integer, primary key): Unique identifier for the listing
- listing_url (text): URL of the listing
- title (text): Car title/name
- price_azn (text): Price in AZN
- make (text): Car manufacturer (e.g., BMW, Mercedes, Toyota)
- model (text): Car model
- year (integer): Manufacturing year
- mileage (text): Odometer reading
- engine_volume (text): Engine displacement
- engine_power (text): Engine power (HP)
- fuel_type (text): Fuel type (Benzin, Dizel, Elektro, Hibrid, etc.)
- transmission (text): Transmission type (Avtomatik, Mexaniki)
- drivetrain (text): Drive type (Ön, Arxa, Tam)
- body_type (text): Body style (Sedan, Offroader, Hetçbek, etc.)
- color (text): Car color
- seats_count (integer): Number of seats
- condition (text): Condition (Sürülmüş, Qəzalı, etc.)
- market (text): Market origin
- is_new (text): New or used
- city (text): Location city
- seller_name (text): Seller name
- seller_phone (jsonb): Seller phone numbers (array)
- description (text): Listing description
- extras (text): Additional features
- views (integer): Number of views
- updated_date (text): Last update date
- posted_date (text): Post date
- is_vip (boolean): VIP listing flag
- is_featured (boolean): Featured listing flag
- is_salon (boolean): Salon listing flag
- has_credit (boolean): Credit available flag
- has_barter (boolean): Barter available flag
- has_vin (boolean): VIN code available flag
- image_urls (text): Car images
- scraped_at (timestamp): Scraping timestamp

IMPORTANT QUERY RULES:
1. Always use "scraping.turbo_az" as the table name (include the schema)
2. For price queries, note that price_azn is stored as text (e.g., "50 000 AZN")
3. Popular makes: Mercedes, BMW, Toyota, Hyundai, Kia, Honda, etc.
4. Years range from ~1980 to 2026
5. Cities include: Bakı, Sumqayıt, Gəncə, Mingəçevir, etc.
6. When counting or aggregating, use appropriate GROUP BY clauses
7. For chart data, return results in a clean format with clear column names
8. Limit results to reasonable numbers (e.g., TOP 10) unless asked otherwise

EXAMPLE QUERIES:
- "How many listings are there?" -> SELECT COUNT(*) as total FROM scraping.turbo_az
- "Top 5 makes" -> SELECT make, COUNT(*) as count FROM scraping.turbo_az GROUP BY make ORDER BY count DESC LIMIT 5
- "Average year by make" -> SELECT make, AVG(year)::int as avg_year FROM scraping.turbo_az WHERE year IS NOT NULL GROUP BY make ORDER BY avg_year DESC LIMIT 10
- "Listings by city" -> SELECT city, COUNT(*) as count FROM scraping.turbo_az WHERE city IS NOT NULL GROUP BY city ORDER BY count DESC

Your task: Convert natural language questions into SQL queries that follow these rules.
Return ONLY the SQL query, nothing else. Do not include markdown formatting or explanations.
`

export async function generateSQLQuery(userQuestion: string): Promise<string> {
  const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" })

  const prompt = `${DATABASE_SCHEMA}

User question: "${userQuestion}"

Generate a SQL query to answer this question. Return ONLY the SQL query.`

  const result = await model.generateContent(prompt)
  const response = result.response
  const query = response.text().trim()

  // Clean up the query (remove markdown code blocks if present)
  let cleanQuery = query
    .replace(/```sql\n?/g, '')
    .replace(/```\n?/g, '')
    .trim()

  return cleanQuery
}

export async function executeSQLQuery(query: string): Promise<any> {
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  })

  try {
    const result = await pool.query(query)
    await pool.end()
    return {
      success: true,
      data: result.rows,
      rowCount: result.rowCount,
    }
  } catch (error: any) {
    await pool.end()
    return {
      success: false,
      error: error.message,
    }
  }
}

export async function answerQuestion(userQuestion: string): Promise<{
  query: string
  result: any
  explanation?: string
}> {
  try {
    // Generate SQL query
    const query = await generateSQLQuery(userQuestion)

    // Execute query
    const result = await executeSQLQuery(query)

    if (!result.success) {
      return {
        query,
        result: {
          success: false,
          error: result.error,
        },
      }
    }

    // Generate explanation
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" })
    const explanationPrompt = `
User asked: "${userQuestion}"

SQL Query executed:
${query}

Query returned ${result.rowCount} rows.

Sample data (first row):
${JSON.stringify(result.data[0] || {}, null, 2)}

Provide a brief, friendly explanation of what the data shows in 1-2 sentences.
`

    const explanationResult = await model.generateContent(explanationPrompt)
    const explanation = explanationResult.response.text()

    return {
      query,
      result,
      explanation,
    }
  } catch (error: any) {
    return {
      query: '',
      result: {
        success: false,
        error: error.message,
      },
    }
  }
}

export function detectChartType(data: any[]): 'bar' | 'line' | 'pie' | 'table' | null {
  if (!data || data.length === 0) return null

  const firstRow = data[0]
  const keys = Object.keys(firstRow)

  // If only one numeric column, suggest pie chart
  const numericKeys = keys.filter(key => typeof firstRow[key] === 'number')

  if (keys.length === 2 && numericKeys.length === 1) {
    // One label, one value - good for pie or bar
    return 'bar'
  }

  if (keys.length > 2 && numericKeys.length >= 2) {
    // Multiple dimensions - line or bar chart
    return 'line'
  }

  return 'table'
}
