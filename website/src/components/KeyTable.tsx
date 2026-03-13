"use client";

import { useState } from "react";
import { Copy, Trash2, Eye, EyeOff } from "lucide-react";
import type { ApiKey } from "@/lib/api";

interface KeyTableProps {
  keys: ApiKey[];
  onDelete: (token: string) => void;
}

export default function KeyTable({ keys, onDelete }: KeyTableProps) {
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());

  const toggleReveal = (token: string) => {
    setRevealedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(token)) next.delete(token);
      else next.add(token);
      return next;
    });
  };

  const copyKey = async (key: string) => {
    await navigator.clipboard.writeText(key);
  };

  if (keys.length === 0) {
    return (
      <div className="text-center py-12 text-[var(--text-secondary)]">
        <p>No API keys yet.</p>
        <p className="text-sm mt-1">Create one to get started.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[var(--text-secondary)] text-xs uppercase">
            <th className="text-left py-3 px-4">Key</th>
            <th className="text-left py-3 px-4">Alias</th>
            <th className="text-right py-3 px-4">Spend</th>
            <th className="text-right py-3 px-4">Budget</th>
            <th className="text-left py-3 px-4">Created</th>
            <th className="text-right py-3 px-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((k) => {
            const revealed = revealedKeys.has(k.token);
            const displayKey = revealed
              ? k.key
              : k.key.slice(0, 8) + "..." + k.key.slice(-4);
            const budget = k.max_budget !== null ? `$${k.max_budget.toFixed(2)}` : "Unlimited";
            const spend = `$${k.spend.toFixed(4)}`;
            const created = k.created_at?.slice(0, 10) || "";

            return (
              <tr
                key={k.token}
                className="border-t border-[var(--border)] hover:bg-[var(--bg-tertiary)]/50"
              >
                <td className="py-3 px-4 font-mono text-xs">{displayKey}</td>
                <td className="py-3 px-4">{k.key_alias || "-"}</td>
                <td className="py-3 px-4 text-right">{spend}</td>
                <td className="py-3 px-4 text-right">{budget}</td>
                <td className="py-3 px-4 text-[var(--text-secondary)]">{created}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => toggleReveal(k.token)}
                      className="p-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      title={revealed ? "Hide key" : "Reveal key"}
                    >
                      {revealed ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                    <button
                      onClick={() => copyKey(k.key)}
                      className="p-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      title="Copy key"
                    >
                      <Copy size={14} />
                    </button>
                    <button
                      onClick={() => onDelete(k.token)}
                      className="p-1 text-[var(--text-secondary)] hover:text-red-400 transition-colors"
                      title="Delete key"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
