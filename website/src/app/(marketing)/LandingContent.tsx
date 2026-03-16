"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import PricingCard from "@/components/PricingCard";
import PricingToggle from "@/components/PricingToggle";
import { TIERS, type BillingPeriod } from "@/lib/stripe";
import { useState } from "react";
import {
  Zap,
  Code,
  Brain,
  Shield,
  ArrowRight,
  Terminal,
  Globe,
  Copy,
  Check,
} from "lucide-react";

type InstallMethod = "curl" | "brew" | "pip" | "uv" | "apt";

const installCommands: Record<InstallMethod, string> = {
  curl: "curl -fsSL minimax.villamarket.ai/install | sh",
  brew: "brew install gastown-publish/mm/mm",
  pip: "pip install minimax-agent",
  uv: "uv tool install minimax-agent",
  apt: "sudo apt install minimax-agent",
};

function InstallTabs() {
  const [method, setMethod] = useState<InstallMethod>("curl");
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(installCommands[method]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div>
      <div className="flex flex-wrap justify-center gap-1 mb-3">
        {(Object.keys(installCommands) as InstallMethod[]).map((m) => (
          <button
            key={m}
            onClick={() => { setMethod(m); setCopied(false); }}
            className={`px-3 py-1.5 text-xs font-mono rounded-md transition-colors ${
              method === m
                ? "bg-sky-600/20 text-sky-400 border border-sky-600/30"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-transparent"
            }`}
          >
            {m}
          </button>
        ))}
      </div>
      <div className="relative max-w-lg mx-auto">
        <pre className="bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg px-4 py-3 text-sm text-left font-mono overflow-x-auto">
          <code>{installCommands[method]}</code>
        </pre>
        <button
          onClick={copy}
          className="absolute top-2 right-2 p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-secondary)] rounded transition-colors"
          title="Copy to clipboard"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}

export default function LandingContent() {
  const { user } = useAuth();
  const [billingPeriod, setBillingPeriod] = useState<BillingPeriod>("monthly");

  const handleTierSelect = (tierId: string) => {
    if (tierId === "free") {
      window.location.href = user ? "/dashboard" : "/login";
      return;
    }
    // Pro/Enterprise — redirect to login if not authed, otherwise dashboard
    window.location.href = user ? "/dashboard" : "/login";
  };

  return (
    <div>
      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 bg-sky-600/10 text-sky-400 text-sm px-4 py-1.5 rounded-full mb-6 border border-sky-600/20">
          <Zap size={14} />
          80.2% SWE-Bench Verified
        </div>
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6">
          <span className="text-sky-400">MiniMax-M2.5</span> API
        </h1>
        <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-8">
          State-of-the-art open-source coding model. 128K context, FP8 precision,
          served on 8x H100 GPUs. OpenAI-compatible API.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <a
            href={user ? "https://app.minimax.villamarket.ai/workspace/chats/new" : "/login?redirect=https://app.minimax.villamarket.ai/workspace/chats/new"}
            className="btn-primary inline-flex items-center gap-2 text-lg px-6 py-3"
          >
            {user ? "Open Chat" : "Get Started"}
            <ArrowRight size={18} />
          </a>
          <Link
            href="/docs"
            className="btn-secondary inline-flex items-center gap-2 text-lg px-6 py-3"
          >
            <Terminal size={16} />
            API Docs
          </Link>
        </div>

        {/* Quick example */}
        <div className="mt-12 max-w-2xl mx-auto text-left">
          <pre className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-4 text-sm overflow-x-auto">
            <code className="text-[var(--text-secondary)]">
              {`curl https://api.minimax.villamarket.ai/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "minimax-m2.5",
    "messages": [{"role": "user", "content": "Write a Python quicksort"}],
    "stream": true
  }'`}
            </code>
          </pre>
        </div>
      </section>

      {/* CLI Install */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
        <div className="card max-w-2xl mx-auto text-center">
          <Terminal size={28} className="text-sky-400 mx-auto mb-3" />
          <h2 className="text-xl font-bold mb-2">Install the CLI</h2>
          <p className="text-sm text-[var(--text-secondary)] mb-4">
            Chat, code, and run skills from your terminal with{" "}
            <code className="text-sky-400 bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded font-mono text-sm">mm</code>
          </p>
          <InstallTabs />
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16">
        <h2 className="text-2xl font-bold text-center mb-12">
          Why MiniMax-M2.5?
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: Brain,
              title: "Top Coding Performance",
              desc: "80.2% on SWE-Bench Verified, 51.3% on Multi-SWE-Bench. Best-in-class for code generation and understanding.",
            },
            {
              icon: Zap,
              title: "128K Context Window",
              desc: "Full 128K token context with FP8 precision on 8x H100 GPUs. Handle entire codebases in a single request.",
            },
            {
              icon: Code,
              title: "OpenAI Compatible",
              desc: "Drop-in replacement for OpenAI API. Works with Claude Code, Cursor, Aider, Continue, and any OpenAI-compatible tool.",
            },
            {
              icon: Terminal,
              title: "Tool Calling & Reasoning",
              desc: "Native function calling with structured outputs. Think blocks show the model's reasoning process.",
            },
            {
              icon: Globe,
              title: "Open Source Model",
              desc: "Built on MiniMaxAI/MiniMax-M2.5, a fully open-source MoE model. No vendor lock-in.",
            },
            {
              icon: Shield,
              title: "Usage-Based Pricing",
              desc: "$0.30/M input tokens, $1.20/M output tokens. Pay only for what you use within your budget.",
            },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card">
              <Icon size={24} className="text-sky-400 mb-3" />
              <h3 className="font-semibold mb-2">{title}</h3>
              <p className="text-sm text-[var(--text-secondary)]">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16" id="pricing">
        <h2 className="text-2xl font-bold text-center mb-4">Pricing</h2>
        <p className="text-center text-[var(--text-secondary)] mb-8">
          Simple, transparent pricing. Start free, scale as you grow.
        </p>
        <PricingToggle value={billingPeriod} onChange={setBillingPeriod} />
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-8">
          {TIERS.map((tier) => (
            <PricingCard
              key={tier.id}
              tier={tier}
              billingPeriod={billingPeriod}
              onSelect={() => handleTierSelect(tier.id)}
            />
          ))}
        </div>
        <p className="text-center text-sm text-[var(--text-secondary)] mt-8">
          Token pricing: $0.30/M input, $1.20/M output. Budget limits prevent unexpected charges.
        </p>
      </section>

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 text-center">
        <div className="card max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold mb-3">Ready to start building?</h2>
          <p className="text-[var(--text-secondary)] mb-6">
            Get your API key in seconds. No credit card required for the free tier.
          </p>
          <Link
            href={user ? "/dashboard" : "/login"}
            className="btn-primary inline-flex items-center gap-2 px-6 py-3"
          >
            {user ? "Go to Dashboard" : "Create Free Account"}
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </div>
  );
}
