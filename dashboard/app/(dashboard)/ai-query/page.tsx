"use client"

import { useState } from "react"
import { useSession, signOut } from "next-auth/react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Brain, ArrowLeft, LogOut } from "lucide-react"
import { useRouter } from "next/navigation"

export default function AIQueryPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [question, setQuestion] = useState("")
  const [result, setResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

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

      // Check for errors in the response
      if (data.result?.error) {
        const errorMsg = data.result.error

        // Check for Gemini API quota errors
        if (errorMsg.includes("quota") || errorMsg.includes("429") || errorMsg.includes("Too Many Requests")) {
          setResult({
            error: "AI Query limit reached. The free tier quota has been exceeded. Please try again later or contact the administrator to upgrade the API plan."
          })
        } else {
          setResult({
            error: errorMsg
          })
        }
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
          <div className="flex items-center justify-between gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
            <div className="flex-1 text-center">
              <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Query Tool
              </h1>
            </div>
            <div className="flex items-center gap-2">
              {session?.user?.role === "admin" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push("/admin")}
                  className="border-blue-200 hover:bg-blue-50 text-xs sm:text-sm h-8 px-2 sm:px-3"
                >
                  Admin Panel
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => signOut({ callbackUrl: "/login" })}
                className="text-xs sm:text-sm h-8 px-2 sm:px-3"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-3 sm:p-4 md:p-6 lg:p-8">
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
