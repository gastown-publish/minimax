"""ACP server bridging MiniMax-M2.5 to Toad and IDEs.

Provides a full coding agent with tool execution:
- bash: Run shell commands
- read_file: Read file contents
- write_file: Write/create files
- list_files: List directory contents
- grep_search: Search file contents with regex
"""

from __future__ import annotations

import asyncio
import json
import os
# B404: subprocess needed for command execution
import subprocess  # nosec: B404
import subprocess
import uuid
from pathlib import Path
from typing import Any


def _is_safe_path(path: Path, allowed_dir: Path) -> bool:
    """Validate path is within allowed directory to prevent path traversal."""
    try:
        resolved = path.resolve()
        allowed = allowed_dir.resolve()
        return str(resolved).startswith(str(allowed))
    except (ValueError, OSError):
        return False

from acp import (
    InitializeResponse,
    LoadSessionResponse,
    NewSessionResponse,
    PROTOCOL_VERSION,
    PromptResponse,
    run_agent,
    update_agent_message_text,
)
from acp.schema import (
    AgentCapabilities,
    Implementation,
    TextContentBlock,
)
from openai import AsyncOpenAI

from .. import __version__
from ..config import get_api_key
from ..api import _base_url
from ..constants import DEFAULT_MODEL, PUBLIC_API_V1
from ..skills import list_skills, load_skill

# ── System prompt ────────────────────────────────────────────────────────

_BASE_SYSTEM_PROMPT = """\
You are MiniMax-M2.5, a powerful AI coding agent running in the user's terminal.

You have access to tools that let you interact with the user's computer:
- bash: Execute shell commands (git, npm, python, curl, etc.)
- read_file: Read file contents
- write_file: Create or overwrite files
- list_files: List directory contents
- grep_search: Search files by content using regex

When the user asks you to do something, USE YOUR TOOLS to accomplish it.
Do NOT say you can't run commands or access files — you CAN and SHOULD.

Guidelines:
- Be concise and direct in your responses
- Use bash for running tests, installing packages, git operations, etc.
- Read files before modifying them
- Show what you did and the results
- If a command fails, try to fix it
- For multi-step tasks, execute each step and verify before continuing
"""

# Default skills injected into every ACP session
_DEFAULT_SKILLS = ["ralph-loop", "code-review", "fix-tests", "git-commit"]


def _build_system_prompt() -> str:
    """Build system prompt with skills injected."""
    # Check environment for skill overrides
    skill_names = os.environ.get("MM_SKILLS", "").split(",") if os.environ.get("MM_SKILLS") else _DEFAULT_SKILLS
    skill_names = [s.strip() for s in skill_names if s.strip()]

    parts = [_BASE_SYSTEM_PROMPT]

    for name in skill_names:
        content = load_skill(name)
        if content:
            parts.append(f"\n## Skill: {name}\n{content}")

    # Include Nori skills if available
    nori_skills_dir = Path.home() / ".nori" / "profiles" / "senior-swe" / "skills"
    if nori_skills_dir.is_dir():
        for skill_dir in sorted(nori_skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            for md_name in ("SKILL.md", "prompt.md"):
                md_file = skill_dir / md_name
                if md_file.exists():
                    parts.append(f"\n## Nori Skill: {skill_dir.name}\n{md_file.read_text()}")
                    break

    return "\n".join(parts)


SYSTEM_PROMPT = _build_system_prompt()

# ── Tool definitions (OpenAI function calling format) ────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command and return stdout/stderr. Use for git, npm, python, curl, compilation, tests, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Returns the file text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative file path to read",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative file path to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: current directory)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search file contents using a regex pattern. Returns matching lines with file paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search in (default: current directory)",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]

# Maximum agent loop iterations to prevent infinite loops
MAX_TOOL_ROUNDS = 25


# ── Tool execution ───────────────────────────────────────────────────────

def _execute_tool(name: str, args: dict, cwd: str) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if name == "bash":
            command = args.get("command", "")
            result = subprocess.run(
                command,
                shell=True,  # nosec: B602 (intentional for bash execution)
                capture_output=True,
                text=True,
                timeout=120,
                cwd=cwd,
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output.strip() or "(no output)"

        elif name == "read_file":
            path = args.get("path", "")
            file_path = Path(path) if os.path.isabs(path) else Path(cwd) / path
            # Validate path is within allowed directory
            if not _is_safe_path(file_path, Path(cwd)):
                return f"Error: Access denied - path outside allowed directory"
            if not file_path.exists():
                return f"Error: File not found: {file_path}"
            if not file_path.is_file():
                return f"Error: Not a file: {file_path}"
            content = file_path.read_text(errors="replace")
            # Truncate very large files
            if len(content) > 100_000:
                content = content[:100_000] + f"\n\n... [truncated, {len(content)} chars total]"
            return content

        elif name == "write_file":
            path = args.get("path", "")
            content = args.get("content", "")
            file_path = Path(path) if os.path.isabs(path) else Path(cwd) / path
            # Validate path is within allowed directory
            if not _is_safe_path(file_path, Path(cwd)):
                return f"Error: Access denied - path outside allowed directory"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Written {len(content)} bytes to {file_path}"

        elif name == "list_files":
            path = args.get("path", cwd)
            dir_path = Path(path) if os.path.isabs(path) else Path(cwd) / path
            if not dir_path.exists():
                return f"Error: Directory not found: {dir_path}"
            if not dir_path.is_dir():
                return f"Error: Not a directory: {dir_path}"
            entries = sorted(dir_path.iterdir())
            lines = []
            for entry in entries[:200]:  # Limit to 200 entries
                suffix = "/" if entry.is_dir() else ""
                lines.append(f"{entry.name}{suffix}")
            result = "\n".join(lines)
            if len(entries) > 200:
                result += f"\n... ({len(entries)} total entries)"
            return result or "(empty directory)"

        elif name == "grep_search":
            pattern = args.get("pattern", "")
            path = args.get("path", cwd)
            search_path = Path(path) if os.path.isabs(path) else Path(cwd) / path
            result = subprocess.run(
                ["grep", "-rn", "--include=*", "-E", pattern, str(search_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd,
            )
            output = result.stdout.strip()
            # Truncate large grep results
            if len(output) > 50_000:
                output = output[:50_000] + "\n... [truncated]"
            return output or "(no matches)"

        else:
            return f"Error: Unknown tool: {name}"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out (120s limit)"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


# ── ACP Agent ────────────────────────────────────────────────────────────

class MiniMaxAgent:
    """ACP agent backed by MiniMax-M2.5 with tool execution."""

    def __init__(self) -> None:
        api_key = get_api_key()
        if not api_key:
            import sys
            print("Error: No API key set. Run: mm auth login", file=sys.stderr)
            sys.exit(1)
        # Remote users always use the public API
        base = _base_url(api_key)
        self.client = AsyncOpenAI(
            base_url=f"{base}/v1",
            api_key=api_key,
            timeout=60.0,
        )
        self.sessions: dict[str, list[dict]] = {}
        self.session_cwd: dict[str, str] = {}
        self.conn: Any = None

    def on_connect(self, conn: Any) -> None:
        self.conn = conn

    async def initialize(
        self,
        protocol_version: int,
        client_capabilities: Any = None,
        client_info: Any = None,
        **kwargs: Any,
    ) -> InitializeResponse:
        return InitializeResponse(
            protocol_version=PROTOCOL_VERSION,
            agent_info=Implementation(name="mm", version=__version__),
            agent_capabilities=AgentCapabilities(),
        )

    async def new_session(
        self, cwd: str, mcp_servers: Any = None, **kwargs: Any
    ) -> NewSessionResponse:
        sid = str(uuid.uuid4())
        self.sessions[sid] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        self.session_cwd[sid] = cwd or os.getcwd()
        return NewSessionResponse(session_id=sid)

    async def load_session(
        self, cwd: str, session_id: str, mcp_servers: Any = None, **kwargs: Any
    ) -> LoadSessionResponse | None:
        if session_id in self.sessions:
            return LoadSessionResponse()
        return None

    async def list_sessions(self, cursor: Any = None, cwd: Any = None, **kwargs: Any) -> Any:
        from acp.schema import ListSessionsResponse, SessionInfo
        sessions = [
            SessionInfo(session_id=sid) for sid in self.sessions
        ]
        return ListSessionsResponse(sessions=sessions)

    async def set_session_mode(self, mode_id: str, session_id: str, **kwargs: Any) -> None:
        return None

    async def set_session_model(self, model_id: str, session_id: str, **kwargs: Any) -> None:
        return None

    async def set_config_option(self, config_id: str, session_id: str, value: str, **kwargs: Any) -> None:
        return None

    async def authenticate(self, method_id: str, **kwargs: Any) -> None:
        return None

    async def _send_text(self, session_id: str, text: str) -> None:
        """Send a text update to the client (Toad)."""
        if self.conn:
            await self.conn.session_update(
                session_id=session_id,
                update=update_agent_message_text(text),
            )

    async def prompt(
        self,
        prompt: list,
        session_id: str,
        **kwargs: Any,
    ) -> PromptResponse:
        # Extract text from content blocks
        user_text = ""
        for block in prompt:
            if isinstance(block, TextContentBlock):
                user_text += block.text
            elif isinstance(block, dict) and block.get("type") == "text":
                user_text += block.get("text", "")

        # Initialize session if needed
        if session_id not in self.sessions:
            self.sessions[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT},
            ]
            self.session_cwd[session_id] = os.getcwd()

        cwd = self.session_cwd.get(session_id, os.getcwd())
        self.sessions[session_id].append({"role": "user", "content": user_text})

        # Agent loop: call model → execute tools → repeat until done
        for _round in range(MAX_TOOL_ROUNDS):
            try:
                response = await self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=self.sessions[session_id],
                    tools=TOOLS,
                    max_tokens=8192,
                )
            except Exception as e:
                error_msg = f"API error: {e}"
                await self._send_text(session_id, f"\n\n**{error_msg}**\n\nCheck that the MiniMax API is running and your key is valid (`mm auth status`).")
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": error_msg,
                })
                return PromptResponse(stop_reason="end_turn")

            choice = response.choices[0]
            message = choice.message

            # If model wants to call tools
            if message.tool_calls:
                # Add assistant message with tool calls to history
                self.sessions[session_id].append(message.model_dump())

                # Show the model's reasoning text if any
                if message.content:
                    await self._send_text(session_id, message.content)

                # Execute each tool call
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {}

                    # Show tool invocation to user
                    if fn_name == "bash":
                        cmd = fn_args.get("command", "")
                        await self._send_text(session_id, f"\n\n```bash\n$ {cmd}\n```\n")
                    elif fn_name == "read_file":
                        await self._send_text(session_id, f"\n\n*Reading {fn_args.get('path', '')}...*\n")
                    elif fn_name == "write_file":
                        await self._send_text(session_id, f"\n\n*Writing {fn_args.get('path', '')}...*\n")
                    elif fn_name == "list_files":
                        await self._send_text(session_id, f"\n\n*Listing {fn_args.get('path', cwd)}...*\n")
                    elif fn_name == "grep_search":
                        await self._send_text(session_id, f"\n\n*Searching for `{fn_args.get('pattern', '')}`...*\n")

                    # Execute the tool
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, _execute_tool, fn_name, fn_args, cwd
                    )

                    # Show truncated result
                    display_result = result
                    if len(display_result) > 2000:
                        display_result = display_result[:2000] + "\n... [truncated]"
                    if fn_name == "bash":
                        await self._send_text(session_id, f"\n```\n{display_result}\n```\n")
                    else:
                        await self._send_text(session_id, f"\n{display_result}\n")

                    # Add tool result to history
                    self.sessions[session_id].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Continue the loop — model will see tool results
                continue

            # No tool calls — model is done, send final text
            if message.content:
                await self._send_text(session_id, message.content)
                self.sessions[session_id].append({
                    "role": "assistant",
                    "content": message.content,
                })

            return PromptResponse(stop_reason="end_turn")

        # Hit max rounds
        await self._send_text(session_id, "\n\n*[Reached maximum tool execution rounds]*")
        return PromptResponse(stop_reason="end_turn")

    async def fork_session(self, cwd: str, session_id: str, **kwargs: Any) -> Any:
        from acp.schema import ForkSessionResponse
        new_sid = str(uuid.uuid4())
        if session_id in self.sessions:
            self.sessions[new_sid] = list(self.sessions[session_id])
            self.session_cwd[new_sid] = self.session_cwd.get(session_id, cwd)
        return ForkSessionResponse(session_id=new_sid)

    async def resume_session(self, cwd: str, session_id: str, **kwargs: Any) -> Any:
        from acp.schema import ResumeSessionResponse
        return ResumeSessionResponse()

    async def cancel(self, session_id: str, **kwargs: Any) -> None:
        pass

    async def ext_method(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        return {}

    async def ext_notification(self, method: str, params: dict[str, Any]) -> None:
        pass


async def main() -> None:
    agent = MiniMaxAgent()
    await run_agent(agent)


if __name__ == "__main__":
    asyncio.run(main())
