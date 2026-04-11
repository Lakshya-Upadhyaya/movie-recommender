"use client";

import { Sparkles } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-4 animate-in fade-in-0 slide-in-from-bottom-4 duration-300">
      {/* AI Avatar */}
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center">
        <Sparkles className="w-4 h-4" />
      </div>

      {/* Typing Animation */}
      <div className="bg-card border border-border/50 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex items-center gap-1.5">
          <span
            className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
            style={{ animationDelay: "0ms", animationDuration: "600ms" }}
          />
          <span
            className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
            style={{ animationDelay: "150ms", animationDuration: "600ms" }}
          />
          <span
            className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
            style={{ animationDelay: "300ms", animationDuration: "600ms" }}
          />
        </div>
      </div>
    </div>
  );
}
