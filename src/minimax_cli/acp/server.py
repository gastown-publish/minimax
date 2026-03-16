"""ACP server bridging MiniMax-M2.5 to Toad and IDEs."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from acp import (
    Agent,
    InitializeResponse,
    LoadSessionResponse,
    NewSessionResponse,
    PROTOCOL_VERSION,
    PromptResponse,
    run_agent,
    session_notification,
    update_agent_message_text,
)
from acp.schema import (
    AgentCapabilities,
    Implementation,
    TextContentBlock,
)
from openai import AsyncOpenAI

from ..config import get_api_key
from ..api import _base_url
from ..constants import DEFAULT_MODEL


class MiniMaxAgent:
    """ACP agent backed by MiniMax-M2.5."""

    def __init__(self) -> None:
        api_key = get_api_key()
        base = _base_url(api_key)
        self.client = AsyncOpenAI(
            base_url=f"{base}/v1",
            api_key=api_key or "none",
        )
        self.sessions: dict[str, list[dict]] = {}
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
            agent_info=Implementation(name="mm", version="0.2.0"),
            agent_capabilities=AgentCapabilities(),
        )

    async def new_session(
        self, cwd: str, mcp_servers: Any = None, **kwargs: Any
    ) -> NewSessionResponse:
        sid = str(uuid.uuid4())
        self.sessions[sid] = [
            {
                "role": "system",
                "content": (
                    "You are MiniMax-M2.5, an AI coding agent. "
                    "Help the user with their task. Be concise and direct."
                ),
            }
        ]
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
                {
                    "role": "system",
                    "content": "You are MiniMax-M2.5, an AI coding agent.",
                }
            ]

        self.sessions[session_id].append({"role": "user", "content": user_text})

        # Stream response from MiniMax
        stream = await self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=self.sessions[session_id],
            stream=True,
            max_tokens=8192,
        )

        full_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                full_text += delta.content
                if self.conn:
                    await self.conn.session_update(
                        session_id=session_id,
                        update=update_agent_message_text(delta.content),
                    )

        self.sessions[session_id].append({"role": "assistant", "content": full_text})
        return PromptResponse(stop_reason="end_turn")

    async def fork_session(self, cwd: str, session_id: str, **kwargs: Any) -> Any:
        from acp.schema import ForkSessionResponse
        new_sid = str(uuid.uuid4())
        if session_id in self.sessions:
            self.sessions[new_sid] = list(self.sessions[session_id])
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
