"use client"

import { useState } from "react"
import { signIn } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Car, BarChart3, Brain, TrendingUp, Shield } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    try {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError("Invalid email or password")
      } else {
        router.push("/dashboard")
        router.refresh()
      }
    } catch (error) {
      setError("An error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left Side - Branding & Features */}
      <div className="lg:w-1/2 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-8 lg:p-12 flex flex-col justify-center text-white">
        <div className="max-w-md mx-auto lg:mx-0">
          {/* Logo & Title */}
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Car className="h-10 w-10" />
            </div>
            <div>
              <h1 className="text-3xl lg:text-4xl font-bold">Turbo Analytics</h1>
              <p className="text-blue-100">Car Market Intelligence</p>
            </div>
          </div>

          {/* Description */}
          <p className="text-xl mb-8 text-blue-50">
            Real-time analytics and insights for Azerbaijan's automotive market
          </p>

          {/* Features */}
          <div className="space-y-4">
            <div className="flex items-start gap-3 bg-white/10 backdrop-blur-sm p-4 rounded-lg">
              <BarChart3 className="h-6 w-6 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-lg">Market Analytics</h3>
                <p className="text-sm text-blue-100">Track trends, prices, and inventory across Turbo.az listings</p>
              </div>
            </div>

            <div className="flex items-start gap-3 bg-white/10 backdrop-blur-sm p-4 rounded-lg">
              <Brain className="h-6 w-6 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-lg">AI-Powered Insights</h3>
                <p className="text-sm text-blue-100">Ask questions in natural language and get instant SQL-powered answers</p>
              </div>
            </div>

            <div className="flex items-start gap-3 bg-white/10 backdrop-blur-sm p-4 rounded-lg">
              <TrendingUp className="h-6 w-6 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-lg">Executive Reports</h3>
                <p className="text-sm text-blue-100">Comprehensive market summaries with YoY and MoM analysis</p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-8 grid grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
              <p className="text-3xl font-bold">50K+</p>
              <p className="text-sm text-blue-100">Car Listings Tracked</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
              <p className="text-3xl font-bold">Real-time</p>
              <p className="text-sm text-blue-100">Market Updates</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="lg:w-1/2 flex items-center justify-center p-8 bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
        <Card className="w-full max-w-md shadow-2xl border-gray-200/50">
          <CardHeader className="space-y-1 pb-6">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Welcome Back
              </CardTitle>
            </div>
            <CardDescription className="text-base">
              Sign in to access your analytics dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="admin@turbo.az"
                  required
                  disabled={isLoading}
                  className="h-11 border-gray-300 focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-semibold">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  required
                  disabled={isLoading}
                  className="h-11 border-gray-300 focus:border-blue-500"
                />
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-base font-semibold shadow-lg"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent"></span>
                    Signing In...
                  </span>
                ) : (
                  "Sign In to Dashboard"
                )}
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-center text-gray-500">
                Secure authentication powered by NextAuth
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
