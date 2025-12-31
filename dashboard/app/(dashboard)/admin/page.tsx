"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function AdminPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [users, setUsers] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Admin Panel</h1>
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={() => router.push("/dashboard")}>
              Back to Dashboard
            </Button>
            <span className="text-sm text-gray-600">{session?.user?.email}</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        <Card>
          <CardHeader>
            <CardTitle>User Management</CardTitle>
            <CardDescription>
              Manage users and their roles
            </CardDescription>
          </CardHeader>
          <CardContent>
            {users.length === 0 ? (
              <p className="text-gray-600">No users found</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Name</th>
                      <th className="px-4 py-3 text-left font-semibold">Email</th>
                      <th className="px-4 py-3 text-left font-semibold">Role</th>
                      <th className="px-4 py-3 text-left font-semibold">Created</th>
                      <th className="px-4 py-3 text-left font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">{user.name || "-"}</td>
                        <td className="px-4 py-3">{user.email}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs ${
                            user.role === "admin"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {new Date(user.createdAt).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deleteUser(user.id)}
                            disabled={user.id === session?.user?.id}
                          >
                            Delete
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

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{users.length}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Admin Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {users.filter((u) => u.role === "admin").length}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Regular Users</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {users.filter((u) => u.role === "user").length}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
