"use client"

import { useState } from "react"
import { signOut, useSession } from "next-auth/react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function DashboardPage() {
  const { data: session } = useSession()
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
      setResult(data)
    } catch (error) {
      console.error("Error:", error)
      setResult({ error: "Failed to fetch results" })
    } finally {
      setIsLoading(false)
    }
  }

  const exampleQuestions = [
    "How many total car listings are there?",
    "What are the top 5 most popular car makes?",
    "Show me average year by make (top 10)",
    "How many listings are in Bakı?",
    "What percentage of cars are automatic transmission?",
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Turbo Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {session?.user?.email}
              {session?.user?.role === "admin" && (
                <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Admin</span>
              )}
            </span>
            {session?.user?.role === "admin" && (
              <Button variant="outline" size="sm" onClick={() => window.location.href = "/admin"}>
                Admin Panel
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={() => signOut({ callbackUrl: "/" })}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        {/* AI Query Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>AI-Powered Analytics 🤖</CardTitle>
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
                className="flex-1"
              />
              <Button onClick={handleAskQuestion} disabled={isLoading}>
                {isLoading ? "Thinking..." : "Ask"}
              </Button>
            </div>

            {/* Example Questions */}
            <div>
              <p className="text-sm text-gray-600 mb-2">Example questions:</p>
              <div className="flex flex-wrap gap-2">
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setQuestion(q)}
                    className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Results */}
            {result && (
              <div className="mt-4 space-y-4">
                {result.error ? (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                    <p className="font-semibold">Error:</p>
                    <p className="text-sm">{result.error}</p>
                  </div>
                ) : (
                  <>
                    {/* SQL Query */}
                    {result.query && (
                      <div className="p-4 bg-gray-900 text-gray-100 rounded-lg">
                        <p className="text-xs text-gray-400 mb-2">Generated SQL:</p>
                        <code className="text-sm">{result.query}</code>
                      </div>
                    )}

                    {/* Explanation */}
                    {result.explanation && (
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-900">{result.explanation}</p>
                      </div>
                    )}

                    {/* Data Table */}
                    {result.result?.data && result.result.data.length > 0 && (
                      <div className="border rounded-lg overflow-hidden">
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-100">
                              <tr>
                                {Object.keys(result.result.data[0]).map((key) => (
                                  <th key={key} className="px-4 py-2 text-left font-semibold">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y">
                              {result.result.data.slice(0, 10).map((row: any, i: number) => (
                                <tr key={i} className="hover:bg-gray-50">
                                  {Object.values(row).map((value: any, j: number) => (
                                    <td key={j} className="px-4 py-2">
                                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        {result.result.data.length > 10 && (
                          <div className="px-4 py-2 bg-gray-50 border-t text-sm text-gray-600">
                            Showing 10 of {result.result.data.length} rows
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total Listings</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">13,785</p>
              <p className="text-xs text-gray-600 mt-1">Active listings</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Avg. Year</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">2014</p>
              <p className="text-xs text-gray-600 mt-1">Average car year</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Top Make</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">Mercedes</p>
              <p className="text-xs text-gray-600 mt-1">Most popular</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Cities</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">15+</p>
              <p className="text-xs text-gray-600 mt-1">Locations covered</p>
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Real-time Data</CardTitle>
              <CardDescription>
                Data is updated continuously from the scraper
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-gray-600">
              The dashboard connects directly to the live database with over 13,000 car listings.
              All queries run in real-time against the latest data.
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Insights</CardTitle>
              <CardDescription>
                Ask questions in natural language
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-gray-600">
              Powered by Google Gemini AI, the dashboard can understand your questions and generate
              SQL queries automatically. No need to know SQL!
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
