"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { createKey } from "@/lib/api";
import ChatMessage, { type Message } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ConversationList, {
  type Conversation,
} from "@/components/ConversationList";
import { Settings, X, PanelLeftClose, PanelLeft } from "lucide-react";

const API_BASE =
  process.env.NEXT_PUBLIC_CHAT_API_BASE || "/v1";
const SEARCH_URL =
  process.env.NEXT_PUBLIC_SEARCH_URL || "";

const STORAGE_KEY = "minimax_conversations";
const SETTINGS_KEY = "minimax_chat_settings";
const MAX_TOOL_ITERATIONS = 3;

/** Strip minimax tool-call XML from content and return clean text */
function stripToolCalls(text: string): string {
  // Remove <minimax:tool_call>...</minimax:tool_call> blocks
  let cleaned = text.replace(/<\/?minimax:tool_call>/g, "");
  // Remove <invoke name="...">...</invoke> blocks
  cleaned = cleaned.replace(/<invoke\s+name="[^"]*">[\s\S]*?<\/invoke>/g, "");
  // Remove <FunctionCall>...</FunctionCall> blocks (model sometimes uses this format)
  cleaned = cleaned.replace(/<FunctionCall>[\s\S]*?<\/FunctionCall>/g, "");
  // Remove unclosed <FunctionCall> at end of streaming content
  cleaned = cleaned.replace(/<FunctionCall>[\s\S]*$/g, "");
  // Remove standalone minimax:tool_call text markers
  cleaned = cleaned.replace(/minimax:tool_call/g, "");
  return cleaned.trim();
}

const TOOLS = [
  {
    type: "function" as const,
    function: {
      name: "web_search",
      description:
        "Search the web for current information. Use this when the user asks you to search, look up, or find information online.",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "The search query" },
        },
        required: ["query"],
      },
    },
  },
];

interface PendingToolCall {
  id: string;
  name: string;
  arguments: string;
}

type ApiMessage =
  | { role: "system" | "user"; content: string }
  | { role: "assistant"; content: string; tool_calls?: { id: string; type: "function"; function: { name: string; arguments: string } }[] }
  | { role: "tool"; tool_call_id: string; content: string };

interface StreamResult {
  content: string;
  reasoning: string;
  toolCalls: PendingToolCall[];
}

async function streamCompletion(
  apiMessages: ApiMessage[],
  apiKey: string,
  settings: ChatSettings,
  signal: AbortSignal,
  onDelta: (content: string, reasoning: string) => void,
  noTools?: boolean,
): Promise<StreamResult> {
  const body: Record<string, unknown> = {
    model: settings.model,
    messages: apiMessages,
    stream: true,
    temperature: settings.temperature,
    max_tokens: settings.maxTokens,
  };
  if (!noTools) {
    body.tools = TOOLS;
  }
  const resp = await fetch(`${API_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal,
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.error?.message || `API error ${resp.status}`);
  }

  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let rawContent = "";
  let accReasoning = "";
  const pendingToolCalls: PendingToolCall[] = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;
      const data = trimmed.slice(6);
      if (data === "[DONE]") continue;

      try {
        const parsed = JSON.parse(data);
        const delta = parsed.choices?.[0]?.delta;
        if (!delta) continue;

        // Accumulate tool_calls deltas
        if (delta.tool_calls) {
          for (const tc of delta.tool_calls) {
            const idx = tc.index;
            if (!pendingToolCalls[idx]) {
              pendingToolCalls[idx] = { id: tc.id || "", name: "", arguments: "" };
            }
            if (tc.id) pendingToolCalls[idx].id = tc.id;
            if (tc.function?.name) pendingToolCalls[idx].name = tc.function.name;
            if (tc.function?.arguments) pendingToolCalls[idx].arguments += tc.function.arguments;
          }
        }

        if (delta.reasoning_content) {
          accReasoning += delta.reasoning_content;
        }
        if (delta.content) {
          rawContent += delta.content;
        }

        // Parse <think> tags from content
        let displayContent = rawContent;
        let displayReasoning = accReasoning;
        const thinkStart = rawContent.indexOf("<think>");
        if (thinkStart !== -1) {
          const thinkEnd = rawContent.indexOf("</think>");
          if (thinkEnd !== -1) {
            displayReasoning = rawContent.slice(thinkStart + 7, thinkEnd).trim();
            displayContent = rawContent.slice(thinkEnd + 8).trim();
          } else {
            displayReasoning = rawContent.slice(thinkStart + 7).trim();
            displayContent = "";
          }
        }

        displayContent = stripToolCalls(displayContent);
        displayReasoning = stripToolCalls(displayReasoning);

        onDelta(displayContent, displayReasoning);
      } catch {
        // Skip malformed SSE
      }
    }
  }

  // Final parse of <think> tags
  let finalContent = rawContent;
  let finalReasoning = accReasoning;
  const thinkStart = rawContent.indexOf("<think>");
  if (thinkStart !== -1) {
    const thinkEnd = rawContent.indexOf("</think>");
    if (thinkEnd !== -1) {
      finalReasoning = rawContent.slice(thinkStart + 7, thinkEnd).trim();
      finalContent = rawContent.slice(thinkEnd + 8).trim();
    } else {
      finalReasoning = rawContent.slice(thinkStart + 7).trim();
      finalContent = "";
    }
  }

  // If vLLM didn't produce structured tool_calls but model emitted <FunctionCall> XML,
  // parse them out and create PendingToolCall entries so the tool loop still works.
  if (pendingToolCalls.length === 0) {
    const fcRegex = /<FunctionCall>\s*\{[^}]*'tool'\s*:\s*'([^']+)'[^}]*'args'\s*:\s*'([^']*)'[^}]*\}\s*<\/FunctionCall>/g;
    let match;
    while ((match = fcRegex.exec(rawContent)) !== null) {
      const toolName = match[1] === "google_search" ? "web_search" : match[1];
      const rawArgs = match[2].replace(/^\s*--query\s+/, "").replace(/^["']|["']$/g, "").trim();
      pendingToolCalls.push({
        id: `fc_${Date.now()}_${pendingToolCalls.length}`,
        name: toolName,
        arguments: JSON.stringify({ query: rawArgs }),
      });
    }
  }

  finalContent = stripToolCalls(finalContent);
  finalReasoning = stripToolCalls(finalReasoning);

  return { content: finalContent, reasoning: finalReasoning, toolCalls: pendingToolCalls };
}

async function executeToolCall(tc: PendingToolCall): Promise<string> {
  if (tc.name === "web_search") {
    try {
      const args = JSON.parse(tc.arguments);
      const query = args.query || "";
      const resp = await fetch(
        `${SEARCH_URL}/search?q=${encodeURIComponent(query)}&format=json`,
      );
      if (!resp.ok) return `Search failed: HTTP ${resp.status}`;
      const data = await resp.json();
      const results = (data.results || []).slice(0, 5);
      if (results.length === 0) return "No search results found.";
      return results
        .map(
          (r: { title: string; url: string; content: string }, i: number) =>
            `[${i + 1}] ${r.title}\n${r.url}\n${r.content || ""}`,
        )
        .join("\n\n");
    } catch (e) {
      return `Search error: ${e instanceof Error ? e.message : "Unknown error"}`;
    }
  }
  return `Unknown tool: ${tc.name}`;
}

interface ChatSettings {
  systemPrompt: string;
  temperature: number;
  maxTokens: number;
  model: string;
}

const DEFAULT_SETTINGS: ChatSettings = {
  systemPrompt: "",
  temperature: 0.7,
  maxTokens: 4096,
  model: "minimax-m2.5",
};

function loadConversations(): Conversation[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveConversations(convs: Conversation[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
}

function loadMessages(convId: string): Message[] {
  try {
    return JSON.parse(localStorage.getItem(`minimax_msgs_${convId}`) || "[]");
  } catch {
    return [];
  }
}

function saveMessages(convId: string, msgs: Message[]) {
  localStorage.setItem(`minimax_msgs_${convId}`, JSON.stringify(msgs));
}

function loadSettings(): ChatSettings {
  try {
    return { ...DEFAULT_SETTINGS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export default function ChatPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const [conversations, setConversations] = useState<Conversation[]>(loadConversations);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [keyLoading, setKeyLoading] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [settings, setSettings] = useState<ChatSettings>(loadSettings);
  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.push("/login");
      return;
    }
    // Ensure the user has an API key ready for chat
    (async () => {
      setKeyLoading(true);
      try {
        // Check localStorage first
        const stored: string[] = JSON.parse(localStorage.getItem("minimax_api_keys") || "[]");
        if (stored.length > 0) {
          setApiKey(stored[0]);
          return;
        }
        // No stored key — auto-create one
        const newKey = await createKey();
        if (newKey.key?.startsWith("sk-")) {
          localStorage.setItem("minimax_api_keys", JSON.stringify([newKey.key]));
          setApiKey(newKey.key);
        }
      } catch {
        // Key creation failed (e.g. at limit) — user will see the no-key message
      } finally {
        setKeyLoading(false);
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, loading]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }, [settings]);

  const createConversation = useCallback((): string => {
    const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    const conv: Conversation = {
      id,
      title: "New Chat",
      lastMessage: "",
      updatedAt: Date.now(),
    };
    const updated = [conv, ...conversations];
    setConversations(updated);
    saveConversations(updated);
    setActiveConvId(id);
    setMessages([]);
    return id;
  }, [conversations]);

  const selectConversation = (id: string) => {
    setActiveConvId(id);
    setMessages(loadMessages(id));
  };

  const deleteConversation = (id: string) => {
    const updated = conversations.filter((c) => c.id !== id);
    setConversations(updated);
    saveConversations(updated);
    localStorage.removeItem(`minimax_msgs_${id}`);
    if (activeConvId === id) {
      setActiveConvId(null);
      setMessages([]);
    }
  };

  const handleSend = async (content: string) => {
    if (!apiKey) return;

    let convId = activeConvId;
    if (!convId) {
      convId = createConversation();
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
    };

    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      reasoning: "",
      isStreaming: true,
    };

    const newMessages = [...messages, userMsg, assistantMsg];
    setMessages(newMessages);
    setIsStreaming(true);

    // Build messages array for API
    const apiMessages: ApiMessage[] = [];
    if (settings.systemPrompt) {
      apiMessages.push({ role: "system", content: settings.systemPrompt });
    }
    for (const msg of [...messages, userMsg]) {
      if (msg.role === "system") continue;
      apiMessages.push({ role: msg.role, content: msg.content });
    }

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      let finalContent = "";
      let finalReasoning = "";

      for (let iteration = 0; iteration < MAX_TOOL_ITERATIONS; iteration++) {
        const result = await streamCompletion(
          apiMessages,
          apiKey,
          settings,
          controller.signal,
          (displayContent, displayReasoning) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last.role === "assistant") {
                updated[updated.length - 1] = {
                  ...last,
                  content: displayContent,
                  reasoning: displayReasoning,
                  isStreaming: true,
                };
              }
              return updated;
            });
          },
        );

        finalContent = result.content;
        finalReasoning = result.reasoning;

        // No tool calls — done
        if (result.toolCalls.length === 0) break;

        // Show tool execution UI
        const toolDisplays = result.toolCalls.map((tc) => {
          try {
            const args = JSON.parse(tc.arguments);
            return { name: tc.name, query: args.query || tc.arguments };
          } catch {
            return { name: tc.name, query: tc.arguments };
          }
        });

        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: result.content,
              reasoning: result.reasoning,
              isStreaming: true,
              toolCalls: toolDisplays,
              toolStatus: "executing",
            };
          }
          return updated;
        });

        // Add assistant message with tool_calls to API messages
        apiMessages.push({
          role: "assistant",
          content: result.content || "",
          tool_calls: result.toolCalls.map((tc) => ({
            id: tc.id,
            type: "function" as const,
            function: { name: tc.name, arguments: tc.arguments },
          })),
        });

        // Execute each tool call and add results
        for (const tc of result.toolCalls) {
          const toolResult = await executeToolCall(tc);
          apiMessages.push({
            role: "tool",
            tool_call_id: tc.id,
            content: toolResult,
          });
        }

        // Update UI to show tool execution done, clear content for next stream
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: "",
              toolStatus: "done",
              isStreaming: true,
            };
          }
          return updated;
        });

        // Loop will stream the next completion
      }

      // If we exhausted iterations and content is empty, do one final stream without tools
      // to force the model to generate a text response
      if (!finalContent.trim()) {
        const result = await streamCompletion(
          apiMessages,
          apiKey,
          { ...settings, model: settings.model },
          controller.signal,
          (displayContent, displayReasoning) => {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last.role === "assistant") {
                updated[updated.length - 1] = {
                  ...last,
                  content: displayContent,
                  reasoning: displayReasoning,
                  isStreaming: true,
                };
              }
              return updated;
            });
          },
          true, // noTools flag
        );
        finalContent = result.content;
        finalReasoning = result.reasoning || finalReasoning;
      }

      // Finalize the assistant message
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          updated[updated.length - 1] = {
            ...last,
            content: finalContent,
            reasoning: finalReasoning,
            isStreaming: false,
            toolStatus: last.toolCalls ? "done" : undefined,
          };
        }
        saveMessages(convId!, updated);
        return updated;
      });

      // Update conversation metadata
      const title =
        messages.length === 0
          ? content.slice(0, 50) + (content.length > 50 ? "..." : "")
          : conversations.find((c) => c.id === convId)?.title || "Chat";

      setConversations((prev) => {
        const updated = prev.map((c) =>
          c.id === convId
            ? { ...c, title, lastMessage: finalContent.slice(0, 80), updatedAt: Date.now() }
            : c
        );
        saveConversations(updated);
        return updated;
      });
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
              isStreaming: false,
            };
          }
          return updated;
        });
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
    setIsStreaming(false);
  };

  if (loading || !user) return null;

  return (
    <div className="flex h-[calc(100vh-56px)]">
      {/* Sidebar */}
      {showSidebar && (
        <ConversationList
          conversations={conversations}
          activeId={activeConvId}
          onSelect={selectConversation}
          onNew={createConversation}
          onDelete={deleteConversation}
        />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
              {showSidebar ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
            </button>
            <span className="text-sm font-medium">
              {activeConvId
                ? conversations.find((c) => c.id === activeConvId)?.title || "Chat"
                : "New Chat"}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {keyLoading && (
              <span className="text-xs text-[var(--text-secondary)]">Setting up...</span>
            )}
            {!keyLoading && !apiKey && (
              <span className="text-xs text-red-400">No API key — <a href="/dashboard" className="underline">create one in Dashboard</a></span>
            )}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-1.5 transition-colors ${
                showSettings
                  ? "text-sky-400"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              <Settings size={18} />
            </button>
          </div>
        </div>

        {/* Settings panel */}
        {showSettings && (
          <div className="border-b border-[var(--border)] bg-[var(--bg-secondary)] px-4 py-4">
            <div className="max-w-3xl mx-auto space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Chat Settings</h3>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                >
                  <X size={16} />
                </button>
              </div>

              <div>
                <label className="text-xs text-[var(--text-secondary)] block mb-1">
                  System Prompt
                </label>
                <textarea
                  value={settings.systemPrompt}
                  onChange={(e) =>
                    setSettings({ ...settings, systemPrompt: e.target.value })
                  }
                  placeholder="You are a helpful coding assistant..."
                  rows={3}
                  className="input-field text-sm resize-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-[var(--text-secondary)] block mb-1">
                    Model
                  </label>
                  <select
                    value={settings.model}
                    onChange={(e) =>
                      setSettings({ ...settings, model: e.target.value })
                    }
                    className="input-field text-sm"
                  >
                    <option value="minimax-m2.5">minimax-m2.5</option>
                    <option value="MiniMaxAI/MiniMax-M2.5">MiniMaxAI/MiniMax-M2.5</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-[var(--text-secondary)] block mb-1">
                    Temperature ({settings.temperature})
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        temperature: parseFloat(e.target.value),
                      })
                    }
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="text-xs text-[var(--text-secondary)] block mb-1">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    value={settings.maxTokens}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        maxTokens: parseInt(e.target.value) || 4096,
                      })
                    }
                    min={1}
                    max={131072}
                    className="input-field text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4">
          <div className="max-w-3xl mx-auto py-4">
            {messages.length === 0 ? (
              <div className="text-center py-20">
                <h2 className="text-xl font-semibold mb-2">MiniMax-M2.5</h2>
                <p className="text-sm text-[var(--text-secondary)] mb-6">
                  128K context, FP8 precision, 8x H100 GPUs
                </p>
                <div className="grid sm:grid-cols-3 gap-3 max-w-lg mx-auto">
                  {[
                    "Write a Python quicksort with tests",
                    "Explain how transformers work",
                    "Debug this React component",
                  ].map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handleSend(prompt)}
                      disabled={!apiKey || keyLoading}
                      className="text-left text-sm p-3 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg hover:bg-[var(--bg-tertiary)] transition-colors disabled:opacity-50"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <ChatInput
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!apiKey || keyLoading}
        />
      </div>
    </div>
  );
}
