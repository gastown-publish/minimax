import { MessageSquare, Plus, Trash2 } from "lucide-react";

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: number;
}

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: ConversationListProps) {
  return (
    <div className="w-64 border-r border-[var(--border)] bg-[var(--bg-secondary)] flex flex-col h-full">
      <div className="p-3 border-b border-[var(--border)]">
        <button
          onClick={onNew}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm bg-[var(--bg-tertiary)] hover:bg-[#252525] border border-[var(--border)] rounded-lg transition-colors"
        >
          <Plus size={14} />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-[var(--text-secondary)]">
            No conversations yet
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`group flex items-center gap-2 px-3 py-2.5 cursor-pointer border-b border-[var(--border)]/50 transition-colors ${
                activeId === conv.id
                  ? "bg-sky-600/10 border-l-2 border-l-sky-500"
                  : "hover:bg-[var(--bg-tertiary)]"
              }`}
            >
              <MessageSquare size={14} className="text-[var(--text-secondary)] flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm truncate">{conv.title}</div>
                <div className="text-xs text-[var(--text-secondary)] truncate">
                  {conv.lastMessage}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-[var(--text-secondary)] hover:text-red-400 transition-all"
                title="Delete conversation"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
