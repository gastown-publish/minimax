"""MiniMax-M2.5 Admin TUI — create, manage, and monitor API key usage."""

from __future__ import annotations

import os

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Rule,
    Static,
)

LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")


async def api_get(url: str, headers: dict | None = None) -> dict | list | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=headers or {})
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


async def api_post(url: str, data: dict, headers: dict | None = None) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=data, headers=headers or {})
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": str(e)}


async def api_delete(url: str, data: dict, headers: dict | None = None) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.request("DELETE", url, json=data, headers=headers or {})
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {LITELLM_MASTER_KEY}"}


def _selected_token(table: DataTable) -> str | None:
    """Get the token hash from the currently selected row."""
    if table.row_count == 0:
        return None
    try:
        cell_key = table.coordinate_to_cell_key((table.cursor_row, 0))
        return cell_key.row_key.value
    except Exception:
        return None


class MiniMaxAdmin(App):
    """MiniMax-M2.5 Admin — API key management and usage monitoring."""

    TITLE = "MiniMax-M2.5 Admin"
    CSS = """
    Screen { background: $surface; }
    #status { padding: 1 2; }
    #key-output { padding: 0 2; min-height: 3; max-height: 10; }
    .form-row { height: 3; padding: 0 2; }
    .form-row Label { padding: 1 1 0 0; width: auto; }
    .form-row Input { width: 20; margin: 0 1 0 0; }
    .btn-row { height: 3; padding: 0 2; }
    .btn-row Button { margin: 0 1 0 0; }
    DataTable { height: 1fr; margin: 1 2; }
    Rule { margin: 0 2; }
    #total { padding: 1 2; text-style: bold; }
    """

    BINDINGS = [
        Binding("g", "generate_key", "New Key"),
        Binding("v", "view_key", "View Key"),
        Binding("b", "set_budget", "Set Budget"),
        Binding("d", "delete_key", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]

    # Store full keys from generation (only available in current session)
    _generated_keys: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("", id="status")
            yield Rule()
            with Horizontal(classes="form-row"):
                yield Label("Alias:")
                yield Input(placeholder="e.g. john", id="alias-input")
                yield Label("Budget $:")
                yield Input(placeholder="10.00", id="budget-input", value="10")
            with Horizontal(classes="btn-row"):
                yield Button("Generate Key", id="btn-gen", variant="success")
                yield Button("View Key", id="btn-view", variant="primary")
                yield Button("Set Budget", id="btn-budget", variant="warning")
                yield Button("Delete Selected", id="btn-del", variant="error")
                yield Button("Refresh", id="btn-refresh", variant="default")
            yield Static("", id="key-output")
            yield Rule()
            yield DataTable(id="keys-table", cursor_type="row")
            yield Rule()
            yield Static("", id="total")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        table.add_columns("Key", "Alias", "Spend", "Budget", "Remaining", "Created")
        self.call_later(self._load_keys)

    @work(exclusive=True, group="load")
    async def _load_keys(self) -> None:
        status = self.query_one("#status", Static)
        health = await api_get(f"{LITELLM_URL}/health/liveliness")
        if health is None:
            status.update("[red bold]LiteLLM OFFLINE[/] — start with: ./scripts/start-all.sh")
            return
        status.update("[green bold]LiteLLM ONLINE[/] — port 4000")

        data = await api_get(
            f"{LITELLM_URL}/key/list?return_full_object=true", headers=auth_headers()
        )
        table = self.query_one("#keys-table", DataTable)
        table.clear()
        total_label = self.query_one("#total", Static)

        if not data:
            total_label.update("[red]Failed to fetch keys[/]")
            return

        keys = data if isinstance(data, list) else data.get("keys", [])
        total_spend = 0.0

        for k in keys:
            if not isinstance(k, dict):
                continue
            token = k.get("token", k.get("key", ""))
            key_name = k.get("key_name", "")
            display_key = key_name if key_name else (token[:8] + "..." if len(token) > 8 else token)

            alias = k.get("key_alias") or ""
            spend = k.get("spend", 0) or 0
            budget = k.get("max_budget")
            budget_str = f"${budget:.2f}" if budget is not None else "unlimited"
            remaining = f"${budget - spend:.2f}" if budget is not None else "n/a"
            created = (k.get("created_at") or "")[:10]

            total_spend += spend
            table.add_row(
                display_key, alias, f"${spend:.4f}", budget_str, remaining, created,
                key=token,
            )

        total_label.update(f"Keys: {len(keys)}  |  Total spend: ${total_spend:.4f}")

    @work(exclusive=True, group="gen")
    async def _generate_key(self) -> None:
        alias_input = self.query_one("#alias-input", Input)
        budget_input = self.query_one("#budget-input", Input)
        output = self.query_one("#key-output", Static)

        try:
            budget = float(budget_input.value.strip() or "10")
        except ValueError:
            output.update("[red]Invalid budget — enter a number[/]")
            return

        payload: dict = {
            "models": ["minimax-m2.5", "MiniMaxAI/MiniMax-M2.5"],
            "max_budget": budget,
        }
        alias = alias_input.value.strip()
        if alias:
            payload["key_alias"] = alias

        result = await api_post(
            f"{LITELLM_URL}/key/generate", data=payload, headers=auth_headers(),
        )
        if result and "key" in result:
            full_key = result["key"]
            token_hash = result.get("token", "")
            self._generated_keys[token_hash] = full_key
            output.update(
                f"[green bold]New key (copy now — cannot be shown again):[/]\n"
                f"  {full_key}"
            )
            alias_input.value = ""
            self._load_keys()
        else:
            msg = "Key generation failed"
            if result and "error" in result:
                err = result["error"]
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            output.update(f"[red]{msg}[/]")

    @work(exclusive=True, group="budget")
    async def _set_budget(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        budget_input = self.query_one("#budget-input", Input)
        output = self.query_one("#key-output", Static)

        token = _selected_token(table)
        if not token:
            output.update("[yellow]Select a key row first[/]")
            return

        try:
            budget = float(budget_input.value.strip() or "10")
        except ValueError:
            output.update("[red]Invalid budget — enter a number[/]")
            return

        result = await api_post(
            f"{LITELLM_URL}/key/update",
            data={"key": token, "max_budget": budget},
            headers=auth_headers(),
        )
        if result and "error" not in result:
            output.update(f"[green]Budget set to ${budget:.2f}[/]")
            self._load_keys()
        else:
            msg = "Budget update failed"
            if result and "error" in result:
                err = result["error"]
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            output.update(f"[red]{msg}[/]")

    @work(exclusive=True, group="view")
    async def _view_key(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        output = self.query_one("#key-output", Static)

        token = _selected_token(table)
        if not token:
            output.update("[yellow]Select a key row first[/]")
            return

        # Fetch fresh key info
        data = await api_get(
            f"{LITELLM_URL}/key/list?return_full_object=true", headers=auth_headers()
        )
        keys = (data if isinstance(data, list) else data.get("keys", [])) if data else []
        k = next((x for x in keys if isinstance(x, dict) and x.get("token") == token), None)

        if not k:
            output.update("[red]Key not found[/]")
            return

        key_name = k.get("key_name", "unknown")
        alias = k.get("key_alias") or "(none)"
        spend = k.get("spend", 0) or 0
        budget = k.get("max_budget")
        budget_str = f"${budget:.2f}" if budget is not None else "unlimited"
        remaining = f"${budget - spend:.2f}" if budget is not None else "n/a"
        created = (k.get("created_at") or "")[:19].replace("T", " ")
        models = ", ".join(k.get("models") or []) or "all"

        # Check if we have the full key from this session
        full_key = self._generated_keys.get(token)
        if full_key:
            key_line = f"  Key:       {full_key}"
        else:
            key_line = f"  Key:       {key_name}  [dim](full key only shown at creation)[/]"

        output.update(
            f"[bold]Key Details[/]\n"
            f"{key_line}\n"
            f"  Alias:     {alias}\n"
            f"  Budget:    {budget_str}  |  Spend: ${spend:.4f}  |  Remaining: {remaining}\n"
            f"  Models:    {models}\n"
            f"  Created:   {created}"
        )

    @work(exclusive=True, group="del")
    async def _delete_key(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        output = self.query_one("#key-output", Static)

        token = _selected_token(table)
        if not token:
            output.update("[yellow]Select a key row first[/]")
            return

        result = await api_delete(
            f"{LITELLM_URL}/key/delete",
            data={"keys": [token]},
            headers=auth_headers(),
        )
        if result:
            output.update("[yellow]Deleted key[/]")
            self._load_keys()
        else:
            output.update("[red]Delete failed[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-gen":
            self._generate_key()
        elif event.button.id == "btn-view":
            self._view_key()
        elif event.button.id == "btn-budget":
            self._set_budget()
        elif event.button.id == "btn-del":
            self._delete_key()
        elif event.button.id == "btn-refresh":
            self._load_keys()

    def action_generate_key(self) -> None:
        self._generate_key()

    def action_view_key(self) -> None:
        self._view_key()

    def action_set_budget(self) -> None:
        self._set_budget()

    def action_delete_key(self) -> None:
        self._delete_key()

    def action_refresh(self) -> None:
        self._load_keys()


def main():
    app = MiniMaxAdmin()
    app.run()


if __name__ == "__main__":
    main()
