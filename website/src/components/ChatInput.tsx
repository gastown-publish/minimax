import { useState, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isStreaming?: boolean;
  disabled?: boolean;
}

export default function ChatInput({ onSend, onStop, isStreaming, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-[var(--border)] bg-[var(--bg-primary)] px-4 py-3">
      <div className="max-w-3xl mx-auto flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message..."
          rows={1}
          disabled={disabled}
          className="input-field resize-none min-h-[40px] max-h-[200px] flex-1"
        />
        {isStreaming ? (
          <button
            onClick={onStop}
            className="p-2.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors flex-shrink-0"
            title="Stop generating"
          >
            <Square size={18} />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            className="p-2.5 bg-sky-600 hover:bg-sky-500 disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex-shrink-0"
            title="Send message"
          >
            <Send size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
