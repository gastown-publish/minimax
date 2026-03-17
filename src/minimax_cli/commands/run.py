"""Interactive chat REPL with streaming and think-block rendering."""

from __future__ import annotations

import click
from rich.console import Console

from ..config import get_api_key
from ..constants import DEFAULT_MODEL
from ..api import _base_url, _headers, check_health

console = Console()


@click.command()
@click.option("--model", default=DEFAULT_MODEL, help="Model ID to use.")
@click.option("--system", "system_msg", default=None, help="System prompt.")
@click.option("--temperature", type=float, default=0.6, help="Sampling temperature.")
@click.option("--max-tokens", type=int, default=4096, help="Max output tokens.")
def run(model: str, system_msg: str | None, temperature: float, max_tokens: int):
    """Interactive chat REPL with streaming output."""
    from openai import OpenAI

    api_key = get_api_key()
    base = _base_url(api_key)

    if not check_health(api_key):
        if api_key:
            console.print("[red bold]API unreachable.[/] Check your key with: mm auth status")
        else:
            console.print("[red bold]No API key set.[/] Run: mm auth login")
        raise SystemExit(1)

    client = OpenAI(base_url=f"{base}/v1", api_key=api_key or "none")
    messages: list[dict] = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})

    # Show actual endpoint being used
    if "localhost:4000" in base:
        source = "local LiteLLM"
    elif "localhost:8080" in base:
        source = "local vLLM"
    else:
        source = base.replace("https://", "").replace("http://", "")
    console.print(f"[bold]MiniMax-M2.5[/] ({source}) — /exit /clear /system <text>")
    console.print()

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye!")
            break

        if not user_input:
            continue
        if user_input == "/exit":
            console.print("Bye!")
            break
        if user_input == "/clear":
            messages = [m for m in messages if m["role"] == "system"]
            console.print("[dim]History cleared.[/]")
            continue
        if user_input.startswith("/system "):
            sys_text = user_input[8:].strip()
            messages = [m for m in messages if m["role"] != "system"]
            messages.insert(0, {"role": "system", "content": sys_text})
            console.print(f"[dim]System prompt set.[/]")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            full_content = ""
            in_think = False

            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                # Handle reasoning_content (vLLM separates think blocks)
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    if not in_think:
                        console.print("[dim]<think>[/]", end="")
                        in_think = True
                    console.print(f"[dim]{reasoning}[/]", end="", highlight=False)
                    continue

                text = delta.content
                if not text:
                    continue

                # Handle inline <think> tags (some backends)
                if "<think>" in text:
                    parts = text.split("<think>", 1)
                    if parts[0]:
                        console.print(parts[0], end="", highlight=False)
                        full_content += parts[0]
                    console.print("[dim]<think>", end="")
                    in_think = True
                    if parts[1]:
                        console.print(f"[dim]{parts[1]}[/]", end="", highlight=False)
                    continue

                if "</think>" in text:
                    parts = text.split("</think>", 1)
                    if parts[0]:
                        console.print(f"[dim]{parts[0]}[/]", end="", highlight=False)
                    console.print("[dim]</think>[/]", end="")
                    in_think = False
                    if parts[1]:
                        console.print(parts[1], end="", highlight=False)
                        full_content += parts[1]
                    continue

                if in_think:
                    console.print(f"[dim]{text}[/]", end="", highlight=False)
                else:
                    console.print(text, end="", highlight=False)
                    full_content += text

            console.print()  # newline after stream
            if full_content:
                messages.append({"role": "assistant", "content": full_content})

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/]")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/]")
