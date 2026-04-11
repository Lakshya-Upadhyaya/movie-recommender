"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage, Message } from "./chat-message";
import { ChatInput } from "./chat-input";
import { TypingIndicator } from "./typing-indicator";
import { OfflineFallback } from "./offline-fallback";
import { Film } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setIsStreaming(false);
    setIsOffline(false);

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: content.trim(),
          history: messages.map((m) => ({ role: m.role, content: m.content })),
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      // Create AI message placeholder
      const aiMessageId = (Date.now() + 1).toString();
      const aiMessage: Message = {
        id: aiMessageId,
        role: "assistant",
        content: "",
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsStreaming(true);
      setIsLoading(false);

      // Read the stream using ReadableStream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        
        // Parse SSE format: data: {...}\n\n
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") continue;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.token) {
                accumulatedContent += parsed.token;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === aiMessageId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                );
              }
            } catch {
              // If not JSON, treat as plain text token
              accumulatedContent += data;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMessageId
                    ? { ...m, content: accumulatedContent }
                    : m
                )
              );
            }
          }
        }
      }

      setIsStreaming(false);
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        return;
      }
      
      console.error("Chat error:", error);
      setIsOffline(true);
      setIsLoading(false);
      setIsStreaming(false);
      
      // Remove the user message if request failed
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    }
  };

  const handleRetry = () => {
    setIsOffline(false);
  };

  if (isOffline) {
    return <OfflineFallback onRetry={handleRetry} />;
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b border-border/50 bg-card/50 backdrop-blur-sm">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/20">
          <Film className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">CineChat</h1>
          <p className="text-xs text-muted-foreground">
            Your AI movie companion
          </p>
        </div>
      </header>

      {/* Messages Area */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-center">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <Film className="w-10 h-10 text-primary" />
              </div>
              <h2 className="text-2xl font-semibold text-foreground mb-2">
                Welcome to CineChat
              </h2>
              <p className="text-muted-foreground max-w-md leading-relaxed">
                Tell me what kind of movies you enjoy, and I&apos;ll recommend
                the perfect films for your next movie night.
              </p>
              <div className="flex flex-wrap gap-2 mt-6 justify-center">
                {[
                  "Recommend a thriller",
                  "Classic rom-coms",
                  "Movies like Inception",
                  "Best of 2024",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => sendMessage(suggestion)}
                    className="px-4 py-2 text-sm rounded-full bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isLoading && !isStreaming && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <ChatInput onSend={sendMessage} disabled={isLoading || isStreaming} />
    </div>
  );
}
