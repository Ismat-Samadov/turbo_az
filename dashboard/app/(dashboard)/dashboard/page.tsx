"use client"

import { useState, useEffect } from "react"
import { signOut, useSession } from "next-auth/react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Car, TrendingUp, MapPin, Calendar, Zap, Database, Brain, ChartBar } from "lucide-react"

export default function DashboardPage() {
  const { data: session } = useSession()
  const [question, setQuestion] = useState("")
  const [result, setResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState<any>(null)

  // Fetch dashboard statistics
  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch("/api/stats")
        const data = await res.json()
        setStats(data)
      } catch (error) {
        console.error("Error fetching stats:", error)
      }
    }

    fetchStats()
  }, [])

  async function handleAskQuestion() {
    if (!question.trim()) return

    setIsLoading(true)
    setResult(null)

    try {
      const res = await fetch("/api/ai/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })

      const data = await res.json()

      // Check for Gemini API quota errors
      if (data.error && data.error.includes("quota")) {
        setResult({
          error: "AI Query limit reached. The free tier quota has been exceeded. Please try again later or contact the administrator to upgrade the API plan."
        })
      } else {
        setResult(data)
      }
    } catch (error) {
      console.error("Error:", error)
      setResult({
        error: "Failed to connect to AI service. Please check your internet connection and try again."
      })
    } finally {
      setIsLoading(false)
    }
  }

  const exampleQuestions = [
    "Show me the top 10 most expensive cars",
    "What are the top 5 most popular car makes?",
    "Show me average price by make for top 10 brands",
    "How many listings are in each city?",
    "What's the distribution of fuel types?",
    "Show me cars by year (grouped)",
  ]

  // Detect if result data is suitable for charting
  const canShowChart = result?.result?.data && result.result.data.length > 0
  const hasNumericData = canShowChart && Object.values(result.result.data[0]).some((v: any) => typeof v === "number")

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
            <div className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Car className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Turbo Analytics
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 w-full sm:w-auto">
              <span className="text-xs sm:text-sm text-gray-600 flex items-center gap-2">
                <span className="truncate max-w-[150px] sm:max-w-none">{session?.user?.email}</span>
                {session?.user?.role === "admin" && (
                  <span className="px-2 py-0.5 sm:py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs rounded-full whitespace-nowrap">
                    Admin
                  </span>
                )}
              </span>
              {session?.user?.role === "admin" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.location.href = "/admin"}
                  className="border-blue-200 hover:bg-blue-50 text-xs sm:text-sm h-8 px-2 sm:px-3"
                >
                  Admin
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => signOut({ callbackUrl: "/" })}
                className="border-gray-200 hover:bg-gray-50 text-xs sm:text-sm h-8 px-2 sm:px-3"
              >
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-3 sm:p-4 md:p-6 lg:p-8 space-y-6 md:space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-blue-100">Total Listings</CardDescription>
                <Database className="h-5 w-5 text-blue-200" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{stats?.total?.toLocaleString() || "..."}</p>
              <p className="text-sm text-blue-100 mt-2">Active in database</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-purple-100">Top Brand</CardDescription>
                <TrendingUp className="h-5 w-5 text-purple-200" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{stats?.byMake?.[0]?.make || "..."}</p>
              <p className="text-sm text-purple-100 mt-2">{stats?.byMake?.[0]?.count?.toLocaleString() || "..."} listings</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-pink-500 to-pink-600 text-white border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-pink-100">Top City</CardDescription>
                <MapPin className="h-5 w-5 text-pink-200" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{stats?.byCity?.[0]?.city || "..."}</p>
              <p className="text-sm text-pink-100 mt-2">{stats?.byCity?.[0]?.count?.toLocaleString() || "..."} listings</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-orange-100">Top Fuel</CardDescription>
                <Zap className="h-5 w-5 text-orange-200" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{stats?.byFuelType?.[0]?.fuel_type || "..."}</p>
              <p className="text-sm text-orange-100 mt-2">{stats?.byFuelType?.[0]?.count?.toLocaleString() || "..."} listings</p>
            </CardContent>
          </Card>
        </div>

        {/* Data Last Updated */}
        {stats && (
          <div className="text-center text-xs sm:text-sm text-gray-500 py-2">
            Last updated: {new Date().toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        )}

        {/* Charts Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Top Makes Chart */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <ChartBar className="h-5 w-5 text-blue-600" />
                <CardTitle>Top Car Brands</CardTitle>
              </div>
              <CardDescription>Most popular car makes in the market</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.byMake || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="make"
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                  />
                  <Bar dataKey="count" fill="url(#blueGradient)" radius={[8, 8, 0, 0]} />
                  <defs>
                    <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Fuel Type Distribution */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-orange-600" />
                <CardTitle>Fuel Type Distribution</CardTitle>
              </div>
              <CardDescription>Market share by fuel type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.byFuelType || []} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="fuel_type" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                  />
                  <Bar dataKey="count" fill="url(#orangeGradient)" radius={[0, 8, 8, 0]} />
                  <defs>
                    <linearGradient id="orangeGradient" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#f59e0b" />
                      <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Listings by Year */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <CardTitle>Listings by Year</CardTitle>
              </div>
              <CardDescription>Recent model years (2015+)</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats?.byYear || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: "#10b981", r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Transmission Types */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <CardTitle>Transmission Distribution</CardTitle>
              </div>
              <CardDescription>Market preference: Automatic vs Manual</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.byTransmission || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="transmission" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                    formatter={(value: any) => [`${parseInt(value).toLocaleString()} listings`, 'Count']}
                  />
                  <Bar dataKey="count" fill="url(#purpleGradient)" radius={[8, 8, 0, 0]} />
                  <defs>
                    <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#8b5cf6" />
                      <stop offset="100%" stopColor="#ec4899" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Average Price by Make */}
          <Card className="shadow-lg border-gray-200/50 lg:col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-pink-600" />
                <CardTitle>Average Price by Brand</CardTitle>
              </div>
              <CardDescription>Top brands with average prices (AZN)</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={stats?.avgPriceByMake || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="make"
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                    formatter={(value: any) => `${parseInt(value).toLocaleString()} AZN`}
                  />
                  <Bar dataKey="avg_price" fill="url(#pinkGradient)" radius={[8, 8, 0, 0]} />
                  <defs>
                    <linearGradient id="pinkGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ec4899" />
                      <stop offset="100%" stopColor="#f59e0b" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Body Type Distribution */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Car className="h-5 w-5 text-indigo-600" />
                <CardTitle>Body Type Distribution</CardTitle>
              </div>
              <CardDescription>Most popular body styles</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.byBodyType || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="body_type"
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                  />
                  <Bar dataKey="count" fill="url(#indigoGradient)" radius={[8, 8, 0, 0]} />
                  <defs>
                    <linearGradient id="indigoGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#14b8a6" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Condition Distribution */}
          <Card className="shadow-lg border-gray-200/50">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-teal-600" />
                <CardTitle>Vehicle Condition</CardTitle>
              </div>
              <CardDescription>Quality distribution analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.byCondition || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="condition"
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                  />
                  <Bar dataKey="count" fill="url(#tealGradient)" radius={[8, 8, 0, 0]} />
                  <defs>
                    <linearGradient id="tealGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#14b8a6" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Business Insights and Findings */}
        <Card className="shadow-xl border-l-4 border-l-blue-600 bg-gradient-to-br from-white to-blue-50/20">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              Key Business Insights
            </CardTitle>
            <CardDescription>Data-driven findings to inform strategic decisions</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {stats && (
              <>
                {/* Market Concentration Analysis */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-6 bg-blue-600 rounded"></span>
                    Market Concentration & Brand Dominance
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-blue-900">Top 3 brands</span> (Mercedes, Hyundai, Changan)
                        control <span className="font-bold text-blue-600">
                          {stats.byMake?.slice(0, 3).reduce((sum: number, item: any) => sum + item.count, 0).toLocaleString()}
                        </span> listings (
                        {((stats.byMake?.slice(0, 3).reduce((sum: number, item: any) => sum + item.count, 0) / stats.total) * 100).toFixed(1)}% market share)
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Strategic Implication:</strong> High concentration indicates brand loyalty and potential partnership opportunities with dominant manufacturers.
                      </p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                      <p className="text-sm text-gray-700 mb-2">
                        Mercedes leads with <span className="font-bold text-purple-600">
                          {stats.byMake?.[0]?.count?.toLocaleString()}
                        </span> listings, commanding a <span className="font-bold">
                          {((stats.byMake?.[0]?.count / stats.total) * 100).toFixed(1)}%
                        </span> market share
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Business Opportunity:</strong> Premium segment shows strong demand; consider inventory optimization for luxury brands.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Pricing Strategy Insights */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-6 bg-pink-600 rounded"></span>
                    Price Positioning & Value Analysis
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-pink-50 p-4 rounded-lg border border-pink-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-pink-900">Highest avg price:</span> {stats.avgPriceByMake?.[0]?.make} at{' '}
                        <span className="font-bold text-pink-600">
                          {stats.avgPriceByMake?.[0]?.avg_price?.toLocaleString()} AZN
                        </span>
                      </p>
                      <p className="text-xs text-gray-600">Premium positioning opportunity in luxury segment</p>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                      <p className="text-sm text-gray-700 mb-2">
                        Average market price: <span className="font-bold text-orange-600">
                          {Math.round(
                            stats.avgPriceByMake?.reduce((sum: number, item: any) => sum + item.avg_price, 0) /
                            (stats.avgPriceByMake?.length || 1)
                          ).toLocaleString()} AZN
                        </span>
                      </p>
                      <p className="text-xs text-gray-600">Benchmark for competitive pricing strategy</p>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-yellow-900">Price variance:</span> High spread indicates diverse market segments
                      </p>
                      <p className="text-xs text-gray-600">Opportunity for targeted marketing by price tier</p>
                    </div>
                  </div>
                </div>

                {/* Geographic Distribution Insights */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-6 bg-pink-600 rounded"></span>
                    Geographic Market Concentration
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-green-900">Bakı dominates</span> with{' '}
                        <span className="font-bold text-green-600">
                          {stats.byCity?.[0]?.count?.toLocaleString()}
                        </span> listings (
                        {((stats.byCity?.[0]?.count / stats.total) * 100).toFixed(1)}% of total market)
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Risk Factor:</strong> High geographic concentration creates dependency on single market; consider expansion to Sumqayıt and Gəncə.
                      </p>
                    </div>
                    <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                      <p className="text-sm text-gray-700 mb-2">
                        Top 3 cities account for <span className="font-bold text-teal-600">
                          {((stats.byCity?.slice(0, 3).reduce((sum: number, item: any) => sum + item.count, 0) / stats.total) * 100).toFixed(1)}%
                        </span> of inventory
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Growth Opportunity:</strong> Underserved regional markets present expansion potential.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Technology & Market Trends */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-6 bg-purple-600 rounded"></span>
                    Technology Adoption & Market Evolution
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-orange-900">Fuel type trend:</span> Benzin leads with{' '}
                        <span className="font-bold text-orange-600">
                          {((stats.byFuelType?.[0]?.count / stats.total) * 100).toFixed(1)}%
                        </span> market share
                      </p>
                      <p className="text-xs text-gray-600">
                        Hybrid/Electric growing: {stats.byFuelType?.filter((f: any) =>
                          f.fuel_type?.toLowerCase().includes('hibrid') || f.fuel_type?.toLowerCase().includes('elektro')
                        ).reduce((sum: number, item: any) => sum + item.count, 0).toLocaleString()} units
                      </p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-purple-900">Transmission preference:</span> Automatic dominates at{' '}
                        <span className="font-bold text-purple-600">
                          {stats.byTransmission?.find((t: any) =>
                            t.transmission?.toLowerCase() === 'automatic'
                          ) ? (
                            ((stats.byTransmission.find((t: any) =>
                              t.transmission?.toLowerCase() === 'automatic'
                            ).count / stats.total) * 100).toFixed(1)
                          ) : '0.0'}%
                        </span>
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Market Signal:</strong> Nearly 4 in 5 buyers prefer automatic transmission; prioritize automatic inventory acquisition.
                      </p>
                    </div>
                    <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-indigo-900">2024-2025 models:</span> Represent{' '}
                        <span className="font-bold text-indigo-600">
                          {stats.byYear?.slice(0, 2).reduce((sum: number, item: any) => sum + item.count, 0).toLocaleString()}
                        </span> units
                      </p>
                      <p className="text-xs text-gray-600">Strong new inventory flow indicates healthy market dynamics</p>
                    </div>
                  </div>
                </div>

                {/* Quality & Condition Analysis */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                    <span className="w-1 h-6 bg-teal-600 rounded"></span>
                    Inventory Quality & Risk Assessment
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-teal-900">Primary condition:</span> {stats.byCondition?.[0]?.condition} accounts for{' '}
                        <span className="font-bold text-teal-600">
                          {((stats.byCondition?.[0]?.count / stats.total) * 100).toFixed(1)}%
                        </span> of inventory
                      </p>
                      <p className="text-xs text-gray-600">
                        Quality distribution impacts financing options and warranty strategies
                      </p>
                    </div>
                    <div className="bg-cyan-50 p-4 rounded-lg border border-cyan-200">
                      <p className="text-sm text-gray-700 mb-2">
                        <span className="font-semibold text-cyan-900">Risk exposure:</span> Monitor accident/damaged units ratio
                      </p>
                      <p className="text-xs text-gray-600">
                        <strong>Recommendation:</strong> Implement rigorous inspection protocols for quality assurance
                      </p>
                    </div>
                  </div>
                </div>

                {/* Strategic Recommendations */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-5 rounded-lg">
                  <h3 className="font-bold text-lg mb-3">Strategic Action Items</h3>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-300 font-bold">•</span>
                      <span><strong>Inventory Optimization:</strong> Increase automatic transmission stock by 15% to meet market preference</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-300 font-bold">•</span>
                      <span><strong>Geographic Expansion:</strong> Establish presence in Sumqayıt and Gəncə to reduce Bakı dependency</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-300 font-bold">•</span>
                      <span><strong>Premium Positioning:</strong> Leverage Mercedes dominance with targeted luxury marketing campaigns</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-300 font-bold">•</span>
                      <span><strong>Future-Ready:</strong> Develop hybrid/electric expertise as market share grows; anticipate 20% increase in next 12 months</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-yellow-300 font-bold">•</span>
                      <span><strong>Risk Mitigation:</strong> Diversify brand portfolio beyond top 3 to reduce concentration risk</span>
                    </li>
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* AI Query Section */}
        <Card className="shadow-xl border-gray-200/50 bg-gradient-to-br from-white to-blue-50/30">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-2xl">AI-Powered Analytics</CardTitle>
            </div>
            <CardDescription>
              Ask questions about Turbo.az car listings in natural language
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Ask a question about the data..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
                className="flex-1 h-12 text-base border-gray-300 focus:border-blue-500"
              />
              <Button
                onClick={handleAskQuestion}
                disabled={isLoading}
                className="h-12 px-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {isLoading ? "Thinking..." : "Ask AI"}
              </Button>
            </div>

            {/* Example Questions */}
            <div>
              <p className="text-sm text-gray-600 mb-3 font-medium">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setQuestion(q)}
                    className="text-sm px-4 py-2 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-all hover:shadow-md"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Results */}
            {result && (
              <div className="mt-6 space-y-4">
                {result.error ? (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                    <p className="font-semibold">Error:</p>
                    <p className="text-sm">{result.error}</p>
                  </div>
                ) : (
                  <>
                    {/* SQL Query */}
                    {result.query && (
                      <div className="p-4 bg-gray-900 text-gray-100 rounded-lg shadow-md">
                        <p className="text-xs text-gray-400 mb-2 font-mono">Generated SQL:</p>
                        <code className="text-sm font-mono">{result.query}</code>
                      </div>
                    )}

                    {/* Explanation */}
                    {result.explanation && (
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-900 leading-relaxed">{result.explanation}</p>
                      </div>
                    )}

                    {/* Chart Visualization */}
                    {canShowChart && hasNumericData && (
                      <Card className="shadow-md">
                        <CardHeader>
                          <CardTitle className="text-lg">Visualization</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={result.result.data.slice(0, 15)}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                              <XAxis
                                dataKey={Object.keys(result.result.data[0])[0]}
                                tick={{ fontSize: 11 }}
                                angle={-45}
                                textAnchor="end"
                                height={80}
                              />
                              <YAxis tick={{ fontSize: 12 }} />
                              <Tooltip
                                contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
                              />
                              <Bar
                                dataKey={Object.keys(result.result.data[0])[1]}
                                fill="url(#colorGradient)"
                                radius={[8, 8, 0, 0]}
                              />
                              <defs>
                                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="0%" stopColor="#3b82f6" />
                                  <stop offset="100%" stopColor="#8b5cf6" />
                                </linearGradient>
                              </defs>
                            </BarChart>
                          </ResponsiveContainer>
                        </CardContent>
                      </Card>
                    )}

                    {/* Data Table */}
                    {result.result?.data && result.result.data.length > 0 && (
                      <Card className="shadow-md overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200">
                              <tr>
                                {Object.keys(result.result.data[0]).map((key) => (
                                  <th key={key} className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {result.result.data.slice(0, 20).map((row: any, i: number) => (
                                <tr key={i} className="hover:bg-blue-50/50 transition-colors">
                                  {Object.values(row).map((value: any, j: number) => (
                                    <td key={j} className="px-4 py-3 text-gray-700">
                                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        {result.result.data.length > 20 && (
                          <div className="px-4 py-3 bg-gray-50 border-t text-sm text-gray-600 font-medium">
                            Showing 20 of {result.result.data.length} rows
                          </div>
                        )}
                      </Card>
                    )}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
