"""ps and list commands — show running processes and available models."""

from __future__ import annotations

import subprocess
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

from ..constants import VLLM_PID, LITELLM_PID, DEFAULT_MODEL
from ..config import get_api_key
from ..api import check_health, list_models as api_list_models

console = Console()


def _proc_info(pid_file) -> dict | None:
    """Get process info from a PID file."""
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text().strip())
        result = subprocess.run(
            ["ps", "-o", "pid,rss,etime,args", "-p", str(pid)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return None
        lines = result.stdout.strip().splitlines()
        if len(lines) < 2:
            return None
        parts = lines[1].split(None, 3)
        return {
            "pid": int(parts[0]),
            "rss_mb": int(parts[1]) // 1024,
            "uptime": parts[2],
            "cmd": parts[3][:60] if len(parts) > 3 else "",
        }
    except Exception:
        return None


def _gpu_summary() -> list[str]:
    """Get per-GPU memory usage via nvidia-smi."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode != 0:
            return []
        lines = []
        for row in r.stdout.strip().splitlines():
            parts = [p.strip() for p in row.split(",")]
            if len(parts) >= 4:
                lines.append(f"GPU {parts[0]}: {parts[1]}/{parts[2]} MiB ({parts[3]}% util)")
        return lines
    except Exception:
        return []


def _is_server_env() -> bool:
    """Check if we're on the server (PID files or scripts exist)."""
    from ..constants import SCRIPTS_DIR
    return SCRIPTS_DIR.exists()


@click.command()
def ps():
    """Show running processes, GPU usage, and uptime. [server-admin]"""
    if not _is_server_env():
        # Client mode — just show connection status
        api_key = get_api_key()
        base_url = "(not configured)"
        if api_key:
            from ..api import _base_url
            base_url = _base_url(api_key)

        console.print("[bold]MiniMax-M2.5 Status[/]")
        console.print(f"  API Key: {'configured' if api_key else '[yellow]not set[/] — run: mm auth login'}")
        console.print(f"  Endpoint: {base_url}")

        if api_key:
            healthy = check_health(api_key)
            console.print(f"  Status: {'[green]connected[/]' if healthy else '[red]unreachable[/]'}")

        models = api_list_models(api_key) if api_key else []
        if models:
            console.print(f"  Models: {', '.join(m.get('id', '?') for m in models)}")
        return

    # Server mode — full process info
    table = Table(title="MiniMax-M2.5 Status", show_header=True)
    table.add_column("Service", style="bold")
    table.add_column("Status")
    table.add_column("PID")
    table.add_column("Memory")
    table.add_column("Uptime")

    # vLLM
    vllm = _proc_info(VLLM_PID)
    if vllm:
        table.add_row(
            "vLLM (:8080)", "[green]running[/]",
            str(vllm["pid"]), f"{vllm['rss_mb']} MB", vllm["uptime"],
        )
    else:
        healthy = check_health(None)
        status = "[green]running[/] (no PID file)" if healthy else "[red]stopped[/]"
        table.add_row("vLLM (:8080)", status, "-", "-", "-")

    # LiteLLM
    litellm = _proc_info(LITELLM_PID)
    if litellm:
        table.add_row(
            "LiteLLM (:4000)", "[green]running[/]",
            str(litellm["pid"]), f"{litellm['rss_mb']} MB", litellm["uptime"],
        )
    else:
        api_key = get_api_key()
        healthy = check_health(api_key) if api_key else False
        status = "[green]running[/] (no PID file)" if healthy else "[red]stopped[/]"
        table.add_row("LiteLLM (:4000)", status, "-", "-", "-")

    console.print(table)

    # GPU info
    gpus = _gpu_summary()
    if gpus:
        console.print()
        console.print("[bold]GPU Memory[/]")
        for line in gpus:
            console.print(f"  {line}")

    # Model info
    api_key = get_api_key()
    models = api_list_models(api_key)
    if models:
        console.print()
        console.print("[bold]Loaded Models[/]")
        for m in models:
            console.print(f"  {m.get('id', 'unknown')}")


@click.command("list")
def list_models():
    """List available models from the API."""
    api_key = get_api_key()
    models = api_list_models(api_key)
    if not models:
        if not api_key:
            console.print("[yellow]No API key set.[/] Run: mm auth login")
        else:
            console.print("[yellow]No models found.[/] Check your key with: mm auth status")
        raise SystemExit(1)

    table = Table(show_header=True)
    table.add_column("Model ID", style="bold")
    table.add_column("Owner")
    table.add_column("Created")

    for m in models:
        created = m.get("created", "")
        if isinstance(created, (int, float)):
            created = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M")
        table.add_row(m.get("id", ""), m.get("owned_by", ""), str(created))

    console.print(table)
