import { NextResponse } from "next/server"
import { answerQuestion } from "@/lib/gemini"

export async function POST(req: Request) {
  try {
    const { question } = await req.json()

    if (!question) {
      return NextResponse.json({ error: "Question is required" }, { status: 400 })
    }

    const result = await answerQuestion(question)

    return NextResponse.json(result)
  } catch (error: any) {
    console.error("AI Query Error:", error)
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    )
  }
}
