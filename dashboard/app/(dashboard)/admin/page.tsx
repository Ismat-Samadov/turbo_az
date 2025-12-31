"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function AdminPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [users, setUsers] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    } else if (session?.user?.role !== "admin") {
      router.push("/dashboard")
    } else {
      fetchUsers()
    }
  }, [status, session, router])

  async function fetchUsers() {
    setIsLoading(true)
    try {
      const res = await fetch("/api/users")
      if (res.ok) {
        const data = await res.json()
        setUsers(data.users || [])
      }
    } catch (error) {
      console.error("Error fetching users:", error)
    } finally {
      setIsLoading(false)
    }
  }

  async function createUser(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsCreating(true)

    const formData = new FormData(e.currentTarget)
    const name = formData.get("name") as string
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const role = formData.get("role") as string

    try {
      const res = await fetch("/api/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role }),
      })

      if (res.ok) {
        alert("User created successfully")
        setShowCreateForm(false)
        fetchUsers()
        e.currentTarget.reset()
      } else {
        const data = await res.json()
        alert(data.error || "Failed to create user")
      }
    } catch (error) {
      console.error("Error creating user:", error)
      alert("Error creating user")
    } finally {
      setIsCreating(false)
    }
  }

  async function deleteUser(userId: string) {
    if (!confirm("Are you sure you want to delete this user?")) return

    try {
      const res = await fetch(`/api/users/${userId}`, {
        method: "DELETE",
      })

      if (res.ok) {
        alert("User deleted successfully")
        fetchUsers()
      } else {
        alert("Failed to delete user")
      }
    } catch (error) {
      console.error("Error deleting user:", error)
      alert("Error deleting user")
    }
  }

  if (status === "loading" || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading...</p>
      </div>
    )
  }

  if (session?.user?.role !== "admin") {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Admin Panel
                </h1>
                <p className="text-sm text-gray-600">Manage users and permissions</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 px-3 py-1 bg-blue-50 rounded-full border border-blue-200">
                {session?.user?.email}
              </span>
              <Button variant="outline" size="sm" onClick={() => router.push("/dashboard")} className="border-blue-200 hover:bg-blue-50">
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription className="text-blue-100">Total Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{users.length}</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription className="text-purple-100">Admin Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">
                {users.filter((u) => u.role === "admin").length}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-pink-500 to-pink-600 text-white border-0 shadow-lg">
            <CardHeader className="pb-3">
              <CardDescription className="text-pink-100">Regular Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">
                {users.filter((u) => u.role === "user").length}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Create User Form */}
        <Card className="shadow-xl border-gray-200/50">
          <CardHeader>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <CardTitle className="text-xl flex items-center gap-2">
                  <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  Create New User
                </CardTitle>
                <CardDescription>Add a new user to the system with appropriate permissions</CardDescription>
              </div>
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                variant={showCreateForm ? "outline" : "default"}
                className={showCreateForm ? "border-red-200 text-red-600 hover:bg-red-50" : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"}
              >
                {showCreateForm ? "Cancel" : "+ Create User"}
              </Button>
            </div>
          </CardHeader>
          {showCreateForm && (
            <CardContent>
              <form onSubmit={createUser} className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="font-semibold">Full Name</Label>
                    <Input
                      id="name"
                      name="name"
                      type="text"
                      placeholder="John Doe"
                      required
                      disabled={isCreating}
                      className="h-11 border-gray-300 focus:border-blue-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email" className="font-semibold">Email Address</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="john@example.com"
                      required
                      disabled={isCreating}
                      className="h-11 border-gray-300 focus:border-blue-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password" className="font-semibold">Password</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="Minimum 6 characters"
                      required
                      minLength={6}
                      disabled={isCreating}
                      className="h-11 border-gray-300 focus:border-blue-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="role" className="font-semibold">User Role</Label>
                    <select
                      id="role"
                      name="role"
                      defaultValue="user"
                      disabled={isCreating}
                      className="flex h-11 w-full rounded-md border border-gray-300 bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="user">Regular User</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end pt-2">
                  <Button
                    type="submit"
                    disabled={isCreating}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-6"
                  >
                    {isCreating ? (
                      <span className="flex items-center gap-2">
                        <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent"></span>
                        Creating...
                      </span>
                    ) : (
                      "Create User"
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          )}
        </Card>

        <Card className="shadow-xl border-gray-200/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <CardTitle className="text-xl">User Management</CardTitle>
            </div>
            <CardDescription>
              View and manage all system users
            </CardDescription>
          </CardHeader>
          <CardContent>
            {users.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <p className="mt-4 text-gray-600">No users found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">Name</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">Email</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">Role</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">Created</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 uppercase text-xs">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-blue-50/50 transition-colors">
                        <td className="px-4 py-3 font-medium text-gray-900">{user.name || "-"}</td>
                        <td className="px-4 py-3 text-gray-700">{user.email}</td>
                        <td className="px-4 py-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            user.role === "admin"
                              ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                              : "bg-gray-100 text-gray-700"
                          }`}>
                            {user.role === "admin" ? "Administrator" : "Regular User"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {new Date(user.createdAt).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deleteUser(user.id)}
                            disabled={user.id === session?.user?.id}
                            className="bg-red-500 hover:bg-red-600"
                          >
                            {user.id === session?.user?.id ? "Current User" : "Delete"}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
