import { NextRequest } from "next/server";

// Mock movie recommendations for demo purposes
const movieRecommendations: Record<string, string> = {
  thriller: `Great choice! Here are some must-watch thrillers:

**Psychological Thrillers:**
• **Gone Girl (2014)** - A masterpiece of suspense about a wife's disappearance
• **Shutter Island (2010)** - DiCaprio delivers in this mind-bending mystery
• **Se7en (1995)** - Dark, gritty, and unforgettable

**Action Thrillers:**
• **Mad Max: Fury Road (2015)** - Non-stop adrenaline
• **Sicario (2015)** - Intense cartel drama
• **John Wick (2014)** - Stylish and relentless

Would you like more specific recommendations based on any of these?`,

  "rom-com": `I love classic romantic comedies! Here are timeless picks:

**90s Gems:**
• **When Harry Met Sally (1989)** - The ultimate rom-com blueprint
• **Pretty Woman (1990)** - Julia Roberts at her most charming
• **Notting Hill (1999)** - Hugh Grant + Julia Roberts = magic

**2000s Favorites:**
• **Love Actually (2003)** - Perfect for any season
• **The Proposal (2009)** - Sandra Bullock & Ryan Reynolds chemistry
• **13 Going on 30 (2004)** - Fun and heartwarming

Any particular era or style you prefer?`,

  inception: `If you loved Inception, you'll enjoy these mind-bending films:

**Christopher Nolan's Other Works:**
• **Interstellar (2014)** - Emotional sci-fi epic
• **The Prestige (2006)** - Twists within twists
• **Tenet (2020)** - Time manipulation taken further

**Similar Vibes:**
• **The Matrix (1999)** - The original reality-bender
• **Arrival (2016)** - Intelligent and moving sci-fi
• **Source Code (2011)** - Looping thriller
• **Dark City (1998)** - Underrated noir sci-fi

Which aspect of Inception appeals to you most - the dreams, the heist, or the emotional core?`,

  default: `I'd be happy to help you find the perfect movie! Here are some questions to narrow it down:

**What mood are you in?**
• Looking for something **exciting** (action, thriller)?
• Want to **laugh** (comedy, rom-com)?
• In the mood to **think** (drama, mystery)?
• Ready to be **amazed** (sci-fi, fantasy)?

**Or tell me about:**
• A movie you recently loved
• Your favorite actors/directors
• A specific genre or time period

What sounds good to you?`,
};

function getRecommendation(message: string): string {
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes("thriller")) {
    return movieRecommendations.thriller;
  }
  if (lowerMessage.includes("rom-com") || lowerMessage.includes("romantic") || lowerMessage.includes("comedy")) {
    return movieRecommendations["rom-com"];
  }
  if (lowerMessage.includes("inception") || lowerMessage.includes("mind") || lowerMessage.includes("sci-fi")) {
    return movieRecommendations.inception;
  }
  if (lowerMessage.includes("2024") || lowerMessage.includes("best") || lowerMessage.includes("new")) {
    return `Here are standout films from recent years:

**2024 Highlights:**
• **Dune: Part Two** - Epic sci-fi continuation
• **Poor Things** - Wildly creative and bold
• **Oppenheimer** - Historical masterpiece

**Recent Gems You Might Have Missed:**
• **Everything Everywhere All at Once (2022)** - Genre-defying brilliance
• **The Banshees of Inisherin (2022)** - Dark comedy perfection
• **Past Lives (2023)** - Quietly devastating romance

Want me to dive deeper into any of these or explore a specific genre?`;
  }
  
  return movieRecommendations.default;
}

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();
    
    if (!message) {
      return new Response("Message is required", { status: 400 });
    }

    const recommendation = getRecommendation(message);
    
    // Create a readable stream that sends tokens
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Simulate streaming by sending word by word with small delays
        const words = recommendation.split(/(\s+)/);
        
        for (const word of words) {
          await new Promise((resolve) => setTimeout(resolve, 20 + Math.random() * 30));
          const data = `data: ${JSON.stringify({ token: word })}\n\n`;
          controller.enqueue(encoder.encode(data));
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
