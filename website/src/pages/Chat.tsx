import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser } from "../auth";
import { listKeys } from "../api";
import ChatMessage, { type Message } from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import ConversationList, {
  type Conversation,
} from "../components/ConversationList";
import { Settings, X, PanelLeftClose, PanelLeft } from "lucide-react";

const API_BASE =
  import.meta.env.VITE_CHAT_API_BASE ||
  "https://api.minimax.villamarket.ai/v1";

const STORAGE_KEY = "minimax_conversations";
const SETTINGS_KEY = "minimax_chat_settings";

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

export default function Chat() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const [conversations, setConversations] = useState<Conversation[]>(loadConversations);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [settings, setSettings] = useState<ChatSettings>(loadSettings);
  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    // Fetch first API key
    listKeys()
      .then((keys) => {
        if (keys.length > 0) setApiKey(keys[0].key);
      })
      .catch(() => {});
  }, []);

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
    const apiMessages: Array<{ role: string; content: string }> = [];
    if (settings.systemPrompt) {
      apiMessages.push({ role: "system", content: settings.systemPrompt });
    }
    // Include conversation history (excluding the current streaming msg)
    for (const msg of [...messages, userMsg]) {
      if (msg.role === "system") continue;
      apiMessages.push({ role: msg.role, content: msg.content });
    }

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const resp = await fetch(`${API_BASE}/chat/completions`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: settings.model,
          messages: apiMessages,
          stream: true,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens,
        }),
        signal: controller.signal,
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error?.message || `API error ${resp.status}`);
      }

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accContent = "";
      let accReasoning = "";

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

            if (delta.reasoning_content) {
              accReasoning += delta.reasoning_content;
            }
            if (delta.content) {
              accContent += delta.content;
            }

            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last.role === "assistant") {
                updated[updated.length - 1] = {
                  ...last,
                  content: accContent,
                  reasoning: accReasoning,
                  isStreaming: true,
                };
              }
              return updated;
            });
          } catch {
            // Skip malformed SSE
          }
        }
      }

      // Finalize
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last.role === "assistant") {
          updated[updated.length - 1] = {
            ...last,
            content: accContent,
            reasoning: accReasoning,
            isStreaming: false,
          };
        }
        // Save to localStorage
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
            ? { ...c, title, lastMessage: accContent.slice(0, 80), updatedAt: Date.now() }
            : c
        );
        saveConversations(updated);
        return updated;
      });
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            updated[updated.length - 1] = {
              ...last,
              content: `Error: ${err.message}`,
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

  if (!user) return null;

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
            {!apiKey && (
              <span className="text-xs text-red-400">No API key — create one in Dashboard</span>
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
                      disabled={!apiKey}
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
          disabled={!apiKey}
        />
      </div>
    </div>
  );
}
