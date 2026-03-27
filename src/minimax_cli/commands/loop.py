"""Ralph Loop — iterative development loop for MiniMax-M2.5."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import click
from rich.console import Console

from ..config import get_api_key
from ..constants import DEFAULT_MODEL

console = Console()

STATE_FILE = ".mm-loop-state.json"


__all__ = ["_git_context","_load_state","_save_state","cmd","loop","_cleanup_state"]
def _git_context() -> str:
    """Gather git diff and file listing for context."""
    parts = []

    # File listing (capped)
    try:
        result = subprocess.run(
            ["find", ".", "-maxdepth", "3", "-not", "-path", "./.git/*", "-type", "f"],
            capture_output=True, text=True, timeout=5,
        )
        files = result.stdout.strip().splitlines()[:100]
        if files:
            parts.append(f"Files in working directory ({len(files)} shown):\n" + "\n".join(files))
    except Exception:
        pass

    # Git diff
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, timeout=5,
        )
        if result.stdout.strip():
            parts.append(f"Git diff (stat):\n{result.stdout.strip()}")
    except Exception:
        pass

    return "\n\n".join(parts)


def _load_state() -> dict:
    p = Path(STATE_FILE)
    if p.exists():
        return json.loads(p.read_text())
    return {"iteration": 0, "started_at": time.time()}


def _save_state(state: dict) -> None:
    Path(STATE_FILE).write_text(json.dumps(state, indent=2) + "\n")


@click.command()
@click.argument("prompt")
@click.option("--max-iterations", "-n", default=100, help="Max loop iterations (default: 100).")
@click.option("--completion-promise", "-p", default=None,
              help="Text the agent outputs when truly done.")
@click.option("--model", default=DEFAULT_MODEL, help="Model ID.")
def loop(prompt: str, max_iterations: int, completion_promise: str | None, model: str):
    """Run iterative development loop (Ralph Loop).

    Sends the same PROMPT repeatedly. The agent sees its previous work
    in files and git. Stops at max iterations or when the agent outputs
    the completion promise text.

    Example:
        mm loop "Fix all failing tests" -n 50 -p "ALL_TESTS_PASS"
    """
    from openai import OpenAI

    from ..api import _base_url

    api_key = get_api_key()
    base = _base_url(api_key)
    client = OpenAI(base_url=f"{base}/v1", api_key=api_key or "none")

    state = _load_state()
    start_iter = state["iteration"]

    console.print(f"[bold]Ralph Loop[/] — iterations {start_iter + 1}..{max_iterations}")
    if completion_promise:
        console.print(f"[dim]Completion promise: {completion_promise}[/]")
    console.print()

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are MiniMax-M2.5, an AI coding agent running in an iterative loop. "
                "Each iteration you receive the same task plus context about the current "
                "state of the codebase. Make incremental progress each iteration. "
                f"When the task is fully complete, include the text: {completion_promise or 'TASK_COMPLETE'}"
            ),
        }
    ]

    for i in range(start_iter, max_iterations):
        state["iteration"] = i + 1
        _save_state(state)

        context = _git_context()
        iter_prompt = (
            f"[Iteration {i + 1}/{max_iterations}]\n\n"
            f"Task: {prompt}\n\n"
            f"{context}"
        )

        messages.append({"role": "user", "content": iter_prompt})

        console.print(f"[bold cyan]── Iteration {i + 1}/{max_iterations} ──[/]")

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=8192,
                temperature=0.6,
                stream=True,
            )

            full_text = ""
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    full_text += delta.content
                    console.print(delta.content, end="", highlight=False)

            console.print("\n")
            messages.append({"role": "assistant", "content": full_text})

            # Check completion promise
            promise = completion_promise or "TASK_COMPLETE"
            if promise in full_text:
                console.print(f"[bold green]Loop complete![/] Agent signaled: {promise}")
                _cleanup_state()
                return

            # Keep conversation manageable — retain system + last 6 messages
            if len(messages) > 7:
                messages = messages[:1] + messages[-6:]

        except KeyboardInterrupt:
            console.print("\n[yellow]Loop interrupted by user.[/]")
            _save_state(state)
            return
        except Exception as e:
            console.print(f"\n[red]Error in iteration {i + 1}: {e}[/]")
            time.sleep(2)

    console.print(f"[yellow]Reached max iterations ({max_iterations}).[/]")
    _cleanup_state()


def _cleanup_state() -> None:
    p = Path(STATE_FILE)
    if p.exists():
        p.unlink()
