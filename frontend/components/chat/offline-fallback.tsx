"use client";

import { WifiOff, RefreshCw } from "lucide-react";

interface OfflineFallbackProps {
  onRetry: () => void;
}

export function OfflineFallback({ onRetry }: OfflineFallbackProps) {
  return (
    <div className="relative flex items-center justify-center h-screen w-full overflow-hidden">
      {/* Background Video with Fallback to Gradient */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
          poster="/fallback-poster.jpg"
        >
          <source
            src="https://assets.mixkit.co/videos/preview/mixkit-clouds-and-blue-sky-2408-large.mp4"
            type="video/mp4"
          />
        </video>
        {/* Cinematic Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/80 to-black/60" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/40" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-lg">
        {/* Icon */}
        <div className="w-24 h-24 rounded-full bg-primary/20 backdrop-blur-sm flex items-center justify-center mb-8 animate-pulse">
          <WifiOff className="w-12 h-12 text-primary" />
        </div>

        {/* Text */}
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight text-balance">
          Backend is offline
        </h1>
        <p className="text-xl text-white/70 mb-8 leading-relaxed">
          Our movie recommendation service is temporarily unavailable. Please
          try again later.
        </p>

        {/* Retry Button */}
        <button
          onClick={onRetry}
          className="flex items-center gap-3 px-8 py-4 bg-primary text-primary-foreground rounded-full text-lg font-medium hover:bg-primary/90 transition-all duration-200 active:scale-95 shadow-xl shadow-primary/20"
        >
          <RefreshCw className="w-5 h-5" />
          Try Again
        </button>

        {/* Additional Info */}
        <p className="mt-12 text-sm text-white/40">
          Error connecting to recommendation service
        </p>
      </div>

      {/* Film Grain Overlay Effect */}
      <div
        className="absolute inset-0 z-20 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}
