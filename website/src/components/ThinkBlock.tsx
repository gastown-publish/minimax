"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Brain } from "lucide-react";

interface ThinkBlockProps {
  content: string;
  isStreaming?: boolean;
}

export default function ThinkBlock({ content, isStreaming }: ThinkBlockProps) {
  const [expanded, setExpanded] = useState(false);

  if (!content) return null;

  return (
    <div className="my-2 border border-sky-500/20 rounded-lg overflow-hidden bg-sky-950/20">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 text-xs text-sky-400 hover:bg-sky-950/30 transition-colors"
      >
        <Brain size={14} className={isStreaming ? "think-pulse" : ""} />
        <span className="font-medium">
          {isStreaming ? "Thinking..." : "Thought process"}
        </span>
        <span className="text-sky-400/50 ml-auto">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
      </button>
      {expanded && (
        <div className="px-3 py-2 text-xs text-[var(--text-secondary)] border-t border-sky-500/10 whitespace-pre-wrap max-h-64 overflow-y-auto">
          {content}
        </div>
      )}
    </div>
  );
}
