"""HTTP helpers for health checks, model listing, and streaming chat."""

from __future__ import annotations

import httpx

from .constants import LITELLM_BASE, PUBLIC_API_BASE, VLLM_BASE


def _base_url(api_key: str | None = None) -> str:
    """Resolve API base URL. Try local first, fall back to public API."""
    if api_key:
        # Try local LiteLLM first, fall back to public
        try:
            r = httpx.get(f"{LITELLM_BASE}/health/liveliness", timeout=2)
            if r.status_code == 200:
                return LITELLM_BASE
        except httpx.ConnectError:
            pass
        return PUBLIC_API_BASE
    # No key — try local vLLM, else public API
    try:
        r = httpx.get(f"{VLLM_BASE}/health", timeout=2)
        if r.status_code == 200:
            return VLLM_BASE
    except httpx.ConnectError:
        pass
    return PUBLIC_API_BASE


def _headers(api_key: str | None = None) -> dict:
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}


def check_health(api_key: str | None = None, timeout: float = 5) -> bool:
    """Return True if the server is healthy."""
    base = _base_url(api_key)
    # Try LiteLLM health endpoint (works on localhost), fall back to /v1/models (works on public API)
    for endpoint in [f"{base}/health/liveliness", f"{base}/v1/models"]:
        try:
            r = httpx.get(endpoint, headers=_headers(api_key), timeout=timeout)
            if r.status_code == 200:
                return True
        except Exception:
            continue
    return False


def list_models(api_key: str | None = None, timeout: float = 5) -> list[dict]:
    """Return list of model dicts from /v1/models."""
    base = _base_url(api_key)
    try:
        r = httpx.get(f"{base}/v1/models", headers=_headers(api_key), timeout=timeout)
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception:
        return []


def verify_key(api_key: str, timeout: float = 5) -> bool:
    """Verify an API key by hitting /v1/models. Tries local, then public API."""
    base = _base_url(api_key)
    try:
        r = httpx.get(
            f"{base}/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        return r.status_code == 200
    except Exception:
        return False


def _email_body(api_key: str, alias: str = "") -> tuple[str, str]:
    """Return (subject, body) for an API key email."""
    from .constants import PUBLIC_API_BASE
    api_v1 = f"{PUBLIC_API_BASE}/v1"
    subject = "Your MiniMax-M2.5 API Key"
    body = (
        f"Hi{' ' + alias if alias else ''},\n\n"
        f"Your MiniMax-M2.5 API key has been created:\n\n"
        f"    {api_key}\n\n"
        f"API Endpoint: {api_v1}\n"
        f"Model: minimax-m2.5\n\n"
        f"Quick test:\n\n"
        f"  curl {api_v1}/chat/completions \\\n"
        f'    -H "Authorization: Bearer {api_key}" \\\n'
        f'    -H "Content-Type: application/json" \\\n'
        f"    -d '{{"
        f'"model": "minimax-m2.5", '
        f'"messages": [{{"role": "user", "content": "Hello!"}}]'
        f"}}'\n\n"
        f"Docs: https://minimax.villamarket.ai/docs\n\n"
        f"— MiniMax-M2.5 Server"
    )
    return subject, body


def send_key_email(email: str, api_key: str, alias: str = "") -> bool:
    """Send API key email via direct MX delivery (no API keys needed).

    Looks up the recipient's MX record and delivers directly via SMTP.
    Falls back to AWS SES if direct delivery fails.
    """
    import smtplib
    from email.mime.text import MIMEText

    from .constants import SES_SENDER

    subject, body = _email_body(api_key, alias)
    sender = f"MiniMax-M2.5 <{SES_SENDER}>"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = email

    # 1. Direct MX delivery — zero config
    try:
        import dns.resolver

        domain = email.split("@")[1]
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange).rstrip(".")

        server = smtplib.SMTP(mx_host, 25, timeout=15)
        server.ehlo("villamarket.ai")
        # Try STARTTLS if supported, but don't fail if it isn't
        try:
            server.starttls()
            server.ehlo("villamarket.ai")
        except smtplib.SMTPNotSupportedError:
            pass
        server.sendmail(SES_SENDER, [email], msg.as_string())
        server.quit()
        return True
    except Exception:
        pass

    # 2. Fallback: AWS SES (works once out of sandbox)
    try:
        import boto3
        from .constants import SES_REGION

        ses = boto3.client("ses", region_name=SES_REGION)
        ses.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        return True
    except Exception:
        pass

    return False
