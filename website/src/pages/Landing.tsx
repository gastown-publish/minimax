import { Link } from "react-router-dom";
import { getStoredUser } from "../auth";
import PricingCard from "../components/PricingCard";
import { TIERS } from "../stripe";
import { redirectToCheckout } from "../stripe";
import {
  Zap,
  Code,
  Brain,
  Shield,
  ArrowRight,
  Terminal,
  Globe,
} from "lucide-react";

export default function Landing() {
  const user = getStoredUser();

  const handleTierSelect = async (tierId: string) => {
    if (!user) {
      window.location.href = "/login";
      return;
    }
    if (tierId === "free") {
      window.location.href = "/dashboard";
      return;
    }
    await redirectToCheckout(tierId);
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
          <Link
            to={user ? "/chat" : "/login"}
            className="btn-primary inline-flex items-center gap-2 text-lg px-6 py-3"
          >
            {user ? "Open Chat" : "Get Started"}
            <ArrowRight size={18} />
          </Link>
          <Link
            to="/docs"
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
        <p className="text-center text-[var(--text-secondary)] mb-12">
          Simple, transparent pricing. Start free, scale as you grow.
        </p>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {TIERS.map((tier) => (
            <PricingCard
              key={tier.id}
              {...tier}
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
            to={user ? "/dashboard" : "/login"}
            className="btn-primary inline-flex items-center gap-2 px-6 py-3"
          >
            {user ? "Go to Dashboard" : "Create Free Account"}
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between text-sm text-[var(--text-secondary)]">
          <span>MiniMax-M2.5 API by villamarket.ai</span>
          <div className="flex gap-4">
            <Link to="/docs" className="hover:text-[var(--text-primary)]">
              Docs
            </Link>
            <a
              href="https://huggingface.co/MiniMaxAI/MiniMax-M2.5"
              target="_blank"
              rel="noopener"
              className="hover:text-[var(--text-primary)]"
            >
              Model
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
