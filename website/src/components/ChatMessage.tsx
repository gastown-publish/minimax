"use client";

import MarkdownRenderer from "./MarkdownRenderer";
import ThinkBlock from "./ThinkBlock";
import { User, Bot, Search } from "lucide-react";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  reasoning?: string;
  isStreaming?: boolean;
  toolCalls?: { name: string; query: string }[];
  toolStatus?: "executing" | "done";
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <span className="text-xs text-[var(--text-secondary)] bg-[var(--bg-tertiary)] px-3 py-1 rounded-full">
          System prompt set
        </span>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 py-4 ${isUser ? "" : ""}`}>
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 ${
          isUser
            ? "bg-sky-600/20 text-sky-400"
            : "bg-emerald-600/20 text-emerald-400"
        }`}
      >
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      <div className="flex-1 min-w-0">
        <div className="text-xs text-[var(--text-secondary)] mb-1 font-medium">
          {isUser ? "You" : "MiniMax-M2.5"}
        </div>

        {message.reasoning && (
          <ThinkBlock
            content={message.reasoning}
            isStreaming={message.isStreaming}
          />
        )}

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex flex-col gap-1 mb-2">
            {message.toolCalls.map((tc, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs text-[var(--text-secondary)] bg-[var(--bg-tertiary)] px-3 py-1.5 rounded-md w-fit"
              >
                <Search
                  size={12}
                  className={message.toolStatus === "executing" ? "animate-pulse" : ""}
                />
                <span>
                  {message.toolStatus === "executing"
                    ? `Searching for "${tc.query}"...`
                    : `Searched for "${tc.query}"`}
                </span>
              </div>
            ))}
          </div>
        )}

        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : message.content ? (
          <MarkdownRenderer content={message.content} />
        ) : message.isStreaming ? (
          <span className="inline-block w-2 h-4 bg-sky-400 animate-pulse rounded-sm" />
        ) : null}
      </div>
    </div>
  );
}
