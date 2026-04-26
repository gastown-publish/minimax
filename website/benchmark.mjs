#!/usr/bin/env node
/**
 * MiniMax-M2.5 Benchmark
 * Tests throughput, latency, context handling, and streaming performance.
 * Runs against the local vLLM endpoint directly (port 8080).
 */

const VLLM_URL = "http://localhost:8080/v1";
const LITELLM_URL = "http://localhost:4000/v1";
const LITELLM_KEY = "YOUR_LITELLM_MASTER_KEY";

async function bench(label, fn) {
  process.stdout.write(`  ${label}... `);
  const start = performance.now();
  try {
    const result = await fn();
    const elapsed = performance.now() - start;
    return { ...result, elapsed };
  } catch (err) {
    const elapsed = performance.now() - start;
    console.log(`FAIL (${(elapsed / 1000).toFixed(1)}s): ${err.message}`);
    return null;
  }
}

async function chatComplete(url, key, messages, opts = {}) {
  const resp = await fetch(`${url}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(key ? { Authorization: `Bearer ${key}` } : {}),
    },
    body: JSON.stringify({
      model: "minimax-m2.5",
      messages,
      ...opts,
    }),
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`${resp.status}: ${body.substring(0, 200)}`);
  }
  return resp.json();
}

async function chatCompleteStream(url, key, messages, opts = {}) {
  const resp = await fetch(`${url}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(key ? { Authorization: `Bearer ${key}` } : {}),
    },
    body: JSON.stringify({
      model: "minimax-m2.5",
      messages,
      stream: true,
      ...opts,
    }),
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`${resp.status}: ${body.substring(0, 200)}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let content = "";
  let reasoning = "";
  let firstTokenTime = null;
  let tokenCount = 0;
  const start = performance.now();

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

        if (delta.content) {
          if (!firstTokenTime) firstTokenTime = performance.now();
          content += delta.content;
          tokenCount++;
        }
        if (delta.reasoning_content) {
          reasoning += delta.reasoning_content;
        }
      } catch {}
    }
  }

  return {
    content,
    reasoning,
    tokenCount,
    firstTokenMs: firstTokenTime ? firstTokenTime - start : null,
  };
}

// ── Main ────────────────────────────────────────────────────────────

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║         MiniMax-M2.5 Performance Benchmark              ║");
console.log("║         8x NVIDIA H100 80GB · FP8 · vLLM 0.17          ║");
console.log("╚══════════════════════════════════════════════════════════╝");
console.log();

// 1. Model Info
console.log("─── Model Info ───");
const models = await fetch(`${VLLM_URL}/models`).then(r => r.json());
const model = models.data[0];
console.log(`  Model ID:        ${model.id}`);
console.log(`  Max context:     ${model.max_model_len.toLocaleString()} tokens`);
console.log(`  Weights path:    ${model.root}`);
console.log();

// 2. Time to First Token (TTFT) — cold
console.log("─── Time to First Token (TTFT) ───");
const ttft = await bench("Short prompt TTFT", async () => {
  const result = await chatCompleteStream(VLLM_URL, null, [
    { role: "user", content: "Hi" },
  ], { max_tokens: 10, temperature: 0 });
  console.log(`${result.firstTokenMs.toFixed(0)}ms (first token), content: "${result.content.replace(/\n/g, ' ').substring(0, 50)}"`);
  return { ttft: result.firstTokenMs };
});

// 3. Output throughput — generate 512 tokens
console.log("\n─── Output Throughput ───");
const tp512 = await bench("Generate ~512 tokens", async () => {
  const start = performance.now();
  const result = await chatComplete(VLLM_URL, null, [
    { role: "user", content: "Write a detailed essay about the history of computing. Be thorough and cover many topics." },
  ], { max_tokens: 512, temperature: 0 });
  const elapsed = performance.now() - start;
  const usage = result.usage;
  const outputToks = usage.completion_tokens;
  const inputToks = usage.prompt_tokens;
  const tokPerSec = outputToks / (elapsed / 1000);
  console.log(`${outputToks} output tokens in ${(elapsed / 1000).toFixed(1)}s = ${tokPerSec.toFixed(1)} tok/s (input: ${inputToks} tokens)`);
  return { outputToks, inputToks, tokPerSec };
});

const tp2048 = await bench("Generate ~2048 tokens", async () => {
  const start = performance.now();
  const result = await chatComplete(VLLM_URL, null, [
    { role: "user", content: "Write a very long and detailed technical tutorial about building a full-stack web application with React, Node.js, and PostgreSQL. Cover setup, authentication, API design, database schema, deployment, testing, and monitoring. Include code examples for each section." },
  ], { max_tokens: 2048, temperature: 0 });
  const elapsed = performance.now() - start;
  const usage = result.usage;
  const outputToks = usage.completion_tokens;
  const inputToks = usage.prompt_tokens;
  const tokPerSec = outputToks / (elapsed / 1000);
  console.log(`${outputToks} output tokens in ${(elapsed / 1000).toFixed(1)}s = ${tokPerSec.toFixed(1)} tok/s (input: ${inputToks} tokens)`);
  return { outputToks, inputToks, tokPerSec };
});

// 4. Streaming throughput
console.log("\n─── Streaming Throughput ───");
const streamBench = await bench("Stream ~512 tokens", async () => {
  const start = performance.now();
  const result = await chatCompleteStream(VLLM_URL, null, [
    { role: "user", content: "Explain quantum computing in detail, covering qubits, entanglement, quantum gates, and algorithms." },
  ], { max_tokens: 512, temperature: 0 });
  const elapsed = performance.now() - start;
  // Count actual output tokens (not SSE chunks)
  const words = result.content.split(/\s+/).length;
  console.log(`TTFT: ${result.firstTokenMs.toFixed(0)}ms, total: ${(elapsed / 1000).toFixed(1)}s, ~${words} words, ${result.tokenCount} chunks`);
  return { ttft: result.firstTokenMs, totalMs: elapsed, words, chunks: result.tokenCount };
});

// 5. Context size test — increasing input lengths
console.log("\n─── Context Length Test ───");
const filler = "The quick brown fox jumps over the lazy dog. ";
for (const targetTokens of [1000, 4000, 16000, 32000]) {
  // ~4 chars per token, ~10 tokens per repetition of filler
  const reps = Math.ceil(targetTokens / 10);
  const longInput = filler.repeat(reps);
  const result = await bench(`~${(targetTokens / 1000).toFixed(0)}K input tokens`, async () => {
    const start = performance.now();
    const resp = await chatComplete(VLLM_URL, null, [
      { role: "user", content: longInput + "\n\nSummarize the above text in one sentence." },
    ], { max_tokens: 100, temperature: 0 });
    const elapsed = performance.now() - start;
    const usage = resp.usage;
    const prefillTokPerSec = usage.prompt_tokens / (elapsed / 1000 - (usage.completion_tokens / (tp512?.tokPerSec || 50)));
    console.log(`input: ${usage.prompt_tokens} tok, output: ${usage.completion_tokens} tok, total: ${(elapsed / 1000).toFixed(1)}s`);
    return { inputToks: usage.prompt_tokens, outputToks: usage.completion_tokens };
  });
}

// 6. LiteLLM overhead
console.log("\n─── LiteLLM Proxy Overhead ───");
const directBench = await bench("Direct vLLM (port 8080)", async () => {
  const start = performance.now();
  await chatComplete(VLLM_URL, null, [
    { role: "user", content: "Say OK" },
  ], { max_tokens: 5, temperature: 0 });
  const elapsed = performance.now() - start;
  console.log(`${elapsed.toFixed(0)}ms`);
  return { ms: elapsed };
});

const proxyBench = await bench("Via LiteLLM (port 4000)", async () => {
  const start = performance.now();
  await chatComplete(LITELLM_URL, LITELLM_KEY, [
    { role: "user", content: "Say OK" },
  ], { max_tokens: 5, temperature: 0 });
  const elapsed = performance.now() - start;
  console.log(`${elapsed.toFixed(0)}ms`);
  return { ms: elapsed };
});

if (directBench && proxyBench) {
  const overhead = proxyBench.ms - directBench.ms;
  console.log(`  Overhead: ${overhead > 0 ? '+' : ''}${overhead.toFixed(0)}ms (${((overhead / directBench.ms) * 100).toFixed(1)}%)`);
}

// 7. Concurrent requests
console.log("\n─── Concurrency ───");
for (const concurrency of [2, 4, 8]) {
  const concBench = await bench(`${concurrency} concurrent requests`, async () => {
    const start = performance.now();
    const promises = Array.from({ length: concurrency }, () =>
      chatComplete(VLLM_URL, null, [
        { role: "user", content: "Count from 1 to 20." },
      ], { max_tokens: 128, temperature: 0 })
    );
    const results = await Promise.all(promises);
    const elapsed = performance.now() - start;
    const totalOutput = results.reduce((sum, r) => sum + r.usage.completion_tokens, 0);
    const totalInput = results.reduce((sum, r) => sum + r.usage.prompt_tokens, 0);
    const aggTokPerSec = totalOutput / (elapsed / 1000);
    console.log(`${totalOutput} total output tok in ${(elapsed / 1000).toFixed(1)}s = ${aggTokPerSec.toFixed(1)} agg tok/s`);
    return { totalOutput, aggTokPerSec };
  });
}

// 8. Thinking mode test
console.log("\n─── Reasoning / Thinking ───");
const thinkBench = await bench("Reasoning with <think> tags", async () => {
  const start = performance.now();
  const result = await chatCompleteStream(VLLM_URL, null, [
    { role: "user", content: "What is 127 * 43? Show your work." },
  ], { max_tokens: 512, temperature: 0.6 });
  const elapsed = performance.now() - start;
  const hasThinking = result.content.includes("<think>") || result.reasoning.length > 0;
  const thinkLen = result.reasoning.length || (result.content.match(/<think>([\s\S]*?)<\/think>/)?.[1]?.length || 0);
  const answer = result.content.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
  console.log(`thinking: ${thinkLen} chars, answer: "${answer.substring(0, 80)}", time: ${(elapsed / 1000).toFixed(1)}s`);
  return { hasThinking, thinkLen, answer: answer.substring(0, 80) };
});

// Summary
console.log("\n╔══════════════════════════════════════════════════════════╗");
console.log("║                     Summary                             ║");
console.log("╠══════════════════════════════════════════════════════════╣");
console.log(`║  Max context:      ${model.max_model_len.toLocaleString().padEnd(12)} tokens               ║`);
if (ttft) console.log(`║  TTFT (short):     ${ttft.ttft.toFixed(0).padEnd(12)} ms                    ║`);
if (tp512) console.log(`║  Throughput 512:   ${tp512.tokPerSec.toFixed(1).padEnd(12)} tok/s                ║`);
if (tp2048) console.log(`║  Throughput 2048:  ${tp2048.tokPerSec.toFixed(1).padEnd(12)} tok/s                ║`);
if (directBench) console.log(`║  Direct latency:   ${directBench.ms.toFixed(0).padEnd(12)} ms                    ║`);
if (proxyBench) console.log(`║  LiteLLM latency:  ${proxyBench.ms.toFixed(0).padEnd(12)} ms                    ║`);
console.log("╚══════════════════════════════════════════════════════════╝");
