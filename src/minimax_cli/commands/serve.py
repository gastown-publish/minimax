"""serve, stop, and logs commands — wrap shell scripts."""

from __future__ import annotations

import os
import subprocess
import sys

import click

from ..constants import SCRIPTS_DIR, VLLM_LOG, LITELLM_LOG


@click.command()
@click.option("--vllm-only", is_flag=True, help="Start vLLM only (no LiteLLM).")
def serve(vllm_only: bool):
    """Start the inference server (vLLM + LiteLLM)."""
    script = SCRIPTS_DIR / ("start.sh" if vllm_only else "start-all.sh")
    if not script.exists():
        click.echo(f"Script not found: {script}", err=True)
        raise SystemExit(1)
    os.execv("/bin/bash", ["bash", str(script)])


@click.command()
def stop():
    """Stop all running servers."""
    script = SCRIPTS_DIR / "stop-all.sh"
    if not script.exists():
        click.echo(f"Script not found: {script}", err=True)
        raise SystemExit(1)
    subprocess.run(["bash", str(script)])


@click.command()
@click.option("--vllm", "target", flag_value="vllm", default=True, help="Tail vLLM logs.")
@click.option("--litellm", "target", flag_value="litellm", help="Tail LiteLLM logs.")
@click.option("-n", "--lines", default=50, help="Number of lines to show.")
@click.option("-f", "--follow", is_flag=True, help="Follow log output.")
def logs(target: str, lines: int, follow: bool):
    """Tail server logs."""
    log_file = VLLM_LOG if target == "vllm" else LITELLM_LOG
    if not log_file.exists():
        click.echo(f"Log file not found: {log_file}")
        raise SystemExit(1)

    cmd = ["tail", f"-n{lines}"]
    if follow:
        cmd.append("-f")
    cmd.append(str(log_file))

    try:
        os.execvp("tail", cmd)
    except KeyboardInterrupt:
        pass
