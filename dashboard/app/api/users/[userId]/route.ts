import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/prisma"

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    // Check if user is authenticated and is an admin
    const session = await auth()

    if (!session || session.user.role !== "admin") {
      return NextResponse.json(
        { error: "Unauthorized. Only admins can delete users." },
        { status: 401 }
      )
    }

    const { userId } = await params

    // Prevent admin from deleting themselves
    if (userId === session.user.id) {
      return NextResponse.json(
        { error: "You cannot delete your own account." },
        { status: 400 }
      )
    }

    // Delete the user
    await prisma.user.delete({
      where: {
        id: userId,
      },
    })

    return NextResponse.json(
      { success: true, message: "User deleted successfully" },
      { status: 200 }
    )
  } catch (error: any) {
    console.error("Error deleting user:", error)

    if (error.code === 'P2025') {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(
      { error: "Failed to delete user" },
      { status: 500 }
    )
  }
}
