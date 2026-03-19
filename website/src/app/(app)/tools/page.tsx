"use client";

import { Blocks, Search, FlaskConical, Bot, ExternalLink } from "lucide-react";

const TOOLS = [
  {
    name: "Dify",
    description:
      "AI workflow builder — create agents, RAG pipelines, and automations",
    url: "https://app.minimax.villamarket.ai/dify",
    icon: Blocks,
    color: "text-indigo-400",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/20",
  },
  {
    name: "SearXNG",
    description: "Private meta-search engine with proxy rotation",
    url: "https://app.minimax.villamarket.ai/search",
    icon: Search,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  {
    name: "DeerFlow",
    description:
      "Deep research agent — automated multi-step investigations",
    url: "https://app.minimax.villamarket.ai",
    icon: FlaskConical,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  {
    name: "OpenClaw",
    description:
      "Autonomous AI agent — browse the web, run commands, manage files, and integrate with messaging platforms",
    url: "https://app.minimax.villamarket.ai/openclaw",
    icon: Bot,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/20",
  },
];

export default function ToolsPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Tools</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">
          Self-hosted AI tools running on the MiniMax GPU cluster
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {TOOLS.map((tool) => {
          const Icon = tool.icon;
          return (
            <div
              key={tool.name}
              className={`card border ${tool.border} flex flex-col`}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className={`p-2 rounded-lg ${tool.bg}`}>
                  <Icon size={24} className={tool.color} />
                </div>
                <h2 className="text-lg font-semibold">{tool.name}</h2>
              </div>
              <p className="text-sm text-[var(--text-secondary)] flex-1 mb-4">
                {tool.description}
              </p>
              <button
                onClick={() => window.open(tool.url, "_blank")}
                className="btn-primary flex items-center justify-center gap-2 w-full"
              >
                Open
                <ExternalLink size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
