"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-tertiary)] rounded transition-colors"
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <div className="relative group">
      <pre className="bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-lg p-4 overflow-x-auto text-sm">
        <code>{code}</code>
      </pre>
      <CopyButton text={code} />
    </div>
  );
}

export default function DocsContent() {
  const [activeSection, setActiveSection] = useState("quickstart");

  const sections = [
    { id: "quickstart", label: "Quick Start" },
    { id: "auth", label: "Authentication" },
    { id: "completions", label: "Chat Completions" },
    { id: "streaming", label: "Streaming" },
    { id: "tools", label: "Tool Calling" },
    { id: "thinking", label: "Think Blocks" },
    { id: "models", label: "Models" },
    { id: "limits", label: "Rate Limits" },
    { id: "cli", label: "CLI (mm)" },
    { id: "integrations", label: "Integrations" },
    { id: "errors", label: "Errors" },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">API Documentation</h1>
      <p className="text-[var(--text-secondary)] mb-8">
        OpenAI-compatible API for MiniMax-M2.5
      </p>

      <div className="flex gap-8">
        {/* Sidebar nav */}
        <nav className="hidden lg:block w-48 flex-shrink-0">
          <div className="sticky top-20 space-y-1">
            {sections.map((s) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                onClick={() => setActiveSection(s.id)}
                className={`block text-sm py-1.5 px-3 rounded transition-colors ${
                  activeSection === s.id
                    ? "text-sky-400 bg-sky-600/10"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {s.label}
              </a>
            ))}
          </div>
        </nav>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-12">
          {/* Quick Start */}
          <section id="quickstart">
            <h2 className="text-xl font-bold mb-4">Quick Start</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              The MiniMax-M2.5 API is fully compatible with the OpenAI API format.
              You can use any OpenAI SDK or tool that supports custom base URLs.
            </p>

            <h3 className="font-semibold mt-6 mb-3">Base URL</h3>
            <CodeBlock code="https://api.minimax.villamarket.ai/v1" />

            <h3 className="font-semibold mt-6 mb-3">cURL</h3>
            <CodeBlock
              code={`curl https://api.minimax.villamarket.ai/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "minimax-m2.5",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'`}
            />

            <h3 className="font-semibold mt-6 mb-3">Python (OpenAI SDK)</h3>
            <CodeBlock
              code={`from openai import OpenAI

client = OpenAI(
    base_url="https://api.minimax.villamarket.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Write a quicksort in Python"}],
)

print(response.choices[0].message.content)`}
            />

            <h3 className="font-semibold mt-6 mb-3">JavaScript/TypeScript</h3>
            <CodeBlock
              code={`import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api.minimax.villamarket.ai/v1",
  apiKey: "YOUR_API_KEY",
});

const response = await client.chat.completions.create({
  model: "minimax-m2.5",
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(response.choices[0].message.content);`}
            />
          </section>

          {/* Authentication */}
          <section id="auth">
            <h2 className="text-xl font-bold mb-4">Authentication</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              All API requests require a Bearer token in the Authorization header.
              Get your API key from the{" "}
              <a href="/dashboard" className="text-sky-400 hover:underline">
                Dashboard
              </a>
              .
            </p>
            <CodeBlock code='Authorization: Bearer sk-...' />
          </section>

          {/* Chat Completions */}
          <section id="completions">
            <h2 className="text-xl font-bold mb-4">Chat Completions</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              Creates a model response for the given chat conversation.
            </p>

            <h3 className="font-semibold mt-6 mb-3">Endpoint</h3>
            <CodeBlock code="POST /v1/chat/completions" />

            <h3 className="font-semibold mt-6 mb-3">Parameters</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Parameter</th>
                    <th className="text-left py-2 px-3">Type</th>
                    <th className="text-left py-2 px-3">Required</th>
                    <th className="text-left py-2 px-3">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["model", "string", "Yes", '"minimax-m2.5"'],
                    ["messages", "array", "Yes", "Array of message objects"],
                    ["temperature", "number", "No", "0-2, default 0.7"],
                    ["max_tokens", "integer", "No", "Max output tokens, default 4096"],
                    ["stream", "boolean", "No", "Enable streaming, default false"],
                    ["tools", "array", "No", "Tool definitions for function calling"],
                    ["top_p", "number", "No", "Nucleus sampling, default 1"],
                    ["stop", "string/array", "No", "Stop sequences"],
                  ].map(([param, type, required, desc]) => (
                    <tr key={param} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-mono text-sky-300">{param}</td>
                      <td className="py-2 px-3 text-[var(--text-secondary)]">{type}</td>
                      <td className="py-2 px-3">{required}</td>
                      <td className="py-2 px-3 text-[var(--text-secondary)]">{desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Streaming */}
          <section id="streaming">
            <h2 className="text-xl font-bold mb-4">Streaming</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              Set <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">stream: true</code> to
              receive Server-Sent Events (SSE). Each event contains a delta with
              the new content.
            </p>
            <CodeBlock
              code={`stream = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "Explain MoE"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
    # Think blocks appear in delta.reasoning_content (custom field)
`}
            />
          </section>

          {/* Tool Calling */}
          <section id="tools">
            <h2 className="text-xl font-bold mb-4">Tool Calling</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              MiniMax-M2.5 supports native function calling via the{" "}
              <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">tools</code> parameter.
            </p>
            <CodeBlock
              code={`response = client.chat.completions.create(
    model="minimax-m2.5",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    }],
)

tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name)       # "get_weather"
print(tool_call.function.arguments)  # '{"city": "Tokyo"}'`}
            />
          </section>

          {/* Think Blocks */}
          <section id="thinking">
            <h2 className="text-xl font-bold mb-4">Think Blocks</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              MiniMax-M2.5 includes internal reasoning in think blocks. When
              streaming, reasoning content appears in{" "}
              <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">
                delta.reasoning_content
              </code>{" "}
              before the main response in <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">delta.content</code>.
            </p>
            <CodeBlock
              code={`# The model automatically uses <think>...</think> blocks
# vLLM separates these into reasoning_content and content

for chunk in stream:
    delta = chunk.choices[0].delta

    # Internal reasoning (optional, may be empty)
    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
        print(f"[thinking] {delta.reasoning_content}", end="")

    # Final response
    if delta.content:
        print(delta.content, end="")`}
            />
          </section>

          {/* Models */}
          <section id="models">
            <h2 className="text-xl font-bold mb-4">Models</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Model ID</th>
                    <th className="text-left py-2 px-3">Context</th>
                    <th className="text-left py-2 px-3">Precision</th>
                    <th className="text-left py-2 px-3">Input Price</th>
                    <th className="text-left py-2 px-3">Output Price</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-[var(--border)]">
                    <td className="py-2 px-3 font-mono text-sky-300">minimax-m2.5</td>
                    <td className="py-2 px-3">128K</td>
                    <td className="py-2 px-3">FP8</td>
                    <td className="py-2 px-3">$0.30/M</td>
                    <td className="py-2 px-3">$1.20/M</td>
                  </tr>
                  <tr className="border-b border-[var(--border)]">
                    <td className="py-2 px-3 font-mono text-sky-300">MiniMaxAI/MiniMax-M2.5</td>
                    <td className="py-2 px-3">128K</td>
                    <td className="py-2 px-3">FP8</td>
                    <td className="py-2 px-3">$0.30/M</td>
                    <td className="py-2 px-3">$1.20/M</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Rate Limits */}
          <section id="limits">
            <h2 className="text-xl font-bold mb-4">Rate Limits</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Tier</th>
                    <th className="text-left py-2 px-3">RPM</th>
                    <th className="text-left py-2 px-3">Budget</th>
                    <th className="text-left py-2 px-3">Keys</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["Free", "5", "$1/mo", "1"],
                    ["Pro", "16", "$20/mo", "5"],
                    ["Enterprise", "Unlimited", "$100/mo", "Unlimited"],
                  ].map(([tier, rpm, budget, keys]) => (
                    <tr key={tier} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-semibold">{tier}</td>
                      <td className="py-2 px-3">{rpm}</td>
                      <td className="py-2 px-3">{budget}</td>
                      <td className="py-2 px-3">{keys}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* CLI */}
          <section id="cli">
            <h2 className="text-xl font-bold mb-4">CLI (mm)</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">mm</code> is
              the official MiniMax terminal agent. Chat, code, run skills, and use the
              Ralph Loop — all from your terminal.
            </p>

            <h3 className="font-semibold mt-6 mb-3">Install</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Method</th>
                    <th className="text-left py-2 px-3">Command</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["curl", "curl -fsSL minimax.villamarket.ai/install | sh"],
                    ["brew", "brew install gastown-publish/mm/mm"],
                    ["pip", "pip install minimax-agent"],
                    ["uv", "uv tool install minimax-agent"],
                    ["pipx", "pipx install minimax-agent"],
                    ["apt", "sudo apt install minimax-agent"],
                  ].map(([method, cmd]) => (
                    <tr key={method} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-semibold">{method}</td>
                      <td className="py-2 px-3 font-mono text-sky-300 flex items-center gap-2">
                        <span>{cmd}</span>
                        <CopyButton text={cmd} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="font-semibold mt-6 mb-3">Quick Start</h3>
            <CodeBlock
              code={`# Authenticate
mm auth login --key YOUR_API_KEY

# Interactive chat
mm run

# Launch Nori TUI (multi-provider AI agent)
mm term

# Launch coding tools pre-configured for MiniMax
mm launch claude
mm launch aider
mm launch nori

# Run a skill
mm skills run code-review "Review my code for bugs"

# Ralph Loop — iterative development
mm loop "Fix all failing tests" -n 50 -p "ALL_TESTS_PASS"`}
            />

            <h3 className="font-semibold mt-6 mb-3">Commands</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Command</th>
                    <th className="text-left py-2 px-3">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["mm run", "Interactive chat REPL"],
                    ["mm term", "Launch Nori TUI"],
                    ["mm launch <tool>", "Launch AI tools (claude, aider, codex, nori, opencode, openclaw)"],
                    ["mm acp", "Start ACP server (for IDEs)"],
                    ["mm loop", "Ralph Loop (iterative dev)"],
                    ["mm skills list", "List bundled skills"],
                    ["mm skills run <name>", "Run a skill"],
                    ["mm auth login", "Store API key"],
                    ["mm setup <tool>", "Configure IDE integration"],
                  ].map(([cmd, desc]) => (
                    <tr key={cmd} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-mono text-sky-300">{cmd}</td>
                      <td className="py-2 px-3 text-[var(--text-secondary)]">{desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h3 className="font-semibold mt-6 mb-3">Bundled Skills</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Skill</th>
                    <th className="text-left py-2 px-3">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["deep-research", "Systematic web research with sources"],
                    ["code-review", "Review for bugs, security, performance"],
                    ["git-commit", "Conventional commit messages"],
                    ["explain-code", "Step-by-step code explanation"],
                    ["fix-tests", "Diagnose and fix failing tests"],
                    ["refactor", "Safe refactoring with verification"],
                    ["write-tests", "Generate tests for existing code"],
                    ["ralph-loop", "Iterative development (100 loops)"],
                  ].map(([skill, desc]) => (
                    <tr key={skill} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-mono text-sky-300">{skill}</td>
                      <td className="py-2 px-3 text-[var(--text-secondary)]">{desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Integrations */}
          <section id="integrations">
            <h2 className="text-xl font-bold mb-4">Integrations</h2>
            <p className="text-[var(--text-secondary)] mb-4">
              MiniMax-M2.5 works with any tool that supports custom OpenAI-compatible endpoints.
            </p>

            <h3 className="font-semibold mt-6 mb-3">Claude Code</h3>
            <p className="text-sm text-[var(--text-secondary)] mb-2">
              Use <code className="text-sky-300 bg-[var(--bg-tertiary)] px-1 rounded">mm launch claude</code> for
              one-step setup, or configure manually:
            </p>
            <CodeBlock
              code={`# Option 1: Use mm launch (recommended)
mm launch claude

# Option 2: Manual setup
export ANTHROPIC_BASE_URL=https://api.minimax.villamarket.ai
export ANTHROPIC_API_KEY=YOUR_API_KEY
export ANTHROPIC_AUTH_TOKEN=YOUR_API_KEY
claude --model minimax-m2.5`}
            />

            <h3 className="font-semibold mt-6 mb-3">Nori</h3>
            <p className="text-sm text-[var(--text-secondary)] mb-2">
              Multi-provider AI TUI that wraps Claude, Gemini, and Codex.
            </p>
            <CodeBlock
              code={`# Option 1: Use mm (recommended)
mm term

# Option 2: Use mm launch
mm launch nori

# Option 3: Manual
npm install -g nori-ai-cli
export ANTHROPIC_BASE_URL=https://api.minimax.villamarket.ai
export ANTHROPIC_API_KEY=YOUR_API_KEY
nori`}
            />

            <h3 className="font-semibold mt-6 mb-3">Cursor</h3>
            <p className="text-sm text-[var(--text-secondary)] mb-2">
              Settings → Models → Add Model → OpenAI Compatible
            </p>
            <CodeBlock
              code={`Base URL: https://api.minimax.villamarket.ai/v1
API Key: YOUR_API_KEY
Model: minimax-m2.5`}
            />

            <h3 className="font-semibold mt-6 mb-3">Aider</h3>
            <CodeBlock
              code={`# Option 1: Use mm launch
mm launch aider

# Option 2: Manual
aider --openai-api-base https://api.minimax.villamarket.ai/v1 \\
      --openai-api-key YOUR_API_KEY \\
      --model openai/minimax-m2.5`}
            />

            <h3 className="font-semibold mt-6 mb-3">Codex CLI</h3>
            <CodeBlock
              code={`# Option 1: Use mm launch
mm launch codex

# Option 2: Manual
export OPENAI_BASE_URL=https://api.minimax.villamarket.ai/v1
export OPENAI_API_KEY=YOUR_API_KEY
codex --model minimax-m2.5`}
            />

            <h3 className="font-semibold mt-6 mb-3">OpenCode</h3>
            <CodeBlock
              code={`# Option 1: Use mm launch
mm launch opencode

# Option 2: Manual
export OPENAI_BASE_URL=https://api.minimax.villamarket.ai/v1
export OPENAI_API_KEY=YOUR_API_KEY
opencode`}
            />

            <h3 className="font-semibold mt-6 mb-3">Continue (VS Code)</h3>
            <CodeBlock
              code={`{
  "models": [{
    "title": "MiniMax-M2.5",
    "provider": "openai",
    "model": "minimax-m2.5",
    "apiBase": "https://api.minimax.villamarket.ai/v1",
    "apiKey": "YOUR_API_KEY"
  }]
}`}
            />

            <h3 className="font-semibold mt-6 mb-3">SillyTavern</h3>
            <CodeBlock
              code={`API Type: Chat Completion (OpenAI)
Custom Endpoint: https://api.minimax.villamarket.ai/v1
API Key: YOUR_API_KEY
Model: minimax-m2.5`}
            />
          </section>

          {/* Errors */}
          <section id="errors">
            <h2 className="text-xl font-bold mb-4">Errors</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs uppercase border-b border-[var(--border)]">
                    <th className="text-left py-2 px-3">Code</th>
                    <th className="text-left py-2 px-3">Meaning</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["401", "Invalid or missing API key"],
                    ["402", "Budget exceeded for this key"],
                    ["429", "Rate limit exceeded"],
                    ["500", "Internal server error"],
                    ["503", "Model is loading or unavailable"],
                  ].map(([code, meaning]) => (
                    <tr key={code} className="border-b border-[var(--border)]">
                      <td className="py-2 px-3 font-mono text-red-400">{code}</td>
                      <td className="py-2 px-3 text-[var(--text-secondary)]">{meaning}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
