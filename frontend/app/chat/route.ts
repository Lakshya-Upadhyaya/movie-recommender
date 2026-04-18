import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { message, history } = await request.json();

    if (!message) {
      return new Response("Message is required", { status: 400 });
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      return new Response("API URL not configured", { status: 500 });
    }

    // Call your FastAPI backend
    const backendRes = await fetch(`${apiUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: message,
        history: history ?? [],
      }),
    });

    if (!backendRes.ok) {
      const err = await backendRes.text();
      return new Response(`Backend error: ${err}`, { status: backendRes.status });
    }

    const data = await backendRes.json();
    const responseText: string = data.response;

    // Re-emit as SSE stream so the frontend stays unchanged
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const words = responseText.split(/(\s+)/);

        for (const word of words) {
          await new Promise((resolve) => setTimeout(resolve, 20 + Math.random() * 30));
          const sseChunk = `data: ${JSON.stringify({ token: word })}\n\n`;
          controller.enqueue(encoder.encode(sseChunk));
        }

        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response("Internal server error", { status: 500 });
  }
}