"""Lambda function for API key management.

Endpoints:
  POST /api/keys    — Generate a new LiteLLM API key
  GET  /api/keys    — List user's keys
  DELETE /api/keys/{id} — Delete a key
"""

import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime


def _validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def _validate_key_alias(alias: str) -> bool:
    """Validate key alias format (alphanumeric, dash, underscore, max 50 chars)."""
    if not alias:
        return True  # Optional field
    return bool(re.match(r"^[a-zA-Z0-9_-]{1,50}$", alias))

LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")

# Tier limits
TIER_LIMITS = {
    "free": {"max_budget": 5.0, "rpm_limit": 5, "max_keys": 5},
    "pro": {"max_budget": 20.0, "rpm_limit": 16, "max_keys": 5},
    "enterprise": {"max_budget": 100.0, "rpm_limit": None, "max_keys": None},
}


def _litellm_request(method, path, data=None):
    """Make a request to the LiteLLM API."""
    url = f"{LITELLM_URL}{path}"
    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"LiteLLM error {e.code}: {body}")


def _get_user_tier(user_id):
    """Get user's subscription tier from DynamoDB."""
    import boto3

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("minimax-users")
    try:
        resp = table.get_item(Key={"user_id": user_id})
        return resp.get("Item", {}).get("tier", "free")
    except Exception:
        return "free"


def _count_user_keys(user_id):
    """Count existing keys for a user."""
    data = _litellm_request("GET", f"/key/list?user_id={user_id}&return_full_object=true")
    keys = data if isinstance(data, list) else data.get("keys", [])
    return len(keys)


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
        },
        "body": json.dumps(body),
    }


def handler(event, context):
    method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method"))
    path = event.get("path", event.get("rawPath", ""))

    # CORS preflight
    if method == "OPTIONS":
        return _response(200, {})

    # Extract user from JWT claims (HTTP API v2 uses authorizer.jwt.claims)
    authorizer = event.get("requestContext", {}).get("authorizer", {})
    claims = authorizer.get("jwt", {}).get("claims", {}) or authorizer.get("claims", {})
    user_id = claims.get("sub", "")
    email = claims.get("email", "")

    if not user_id:
        return _response(401, {"error": "Unauthorized"})

    tier = _get_user_tier(user_id)
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

    if method == "POST" and path.rstrip("/") == "/api/keys":
        # Check key limit
        max_keys = limits["max_keys"]
        if max_keys is not None:
            count = _count_user_keys(user_id)
            if count >= max_keys:
                return _response(400, {"error": f"Key limit reached ({max_keys} for {tier} tier)"})

        # Set budget on the USER, not the key — prevents gaming by creating multiple keys
        try:
            _litellm_request("POST", "/user/new", {
                "user_id": user_id,
                "max_budget": limits["max_budget"],
                "user_email": email,
            })
        except Exception:
            # User may already exist — try update instead
            try:
                _litellm_request("POST", "/user/update", {
                    "user_id": user_id,
                    "max_budget": limits["max_budget"],
                })
            except Exception:
                pass  # Non-fatal — key still works, just no user-level budget cap

        body = json.loads(event.get("body", "{}") or "{}")
        alias = body.get("alias", "")

        # Validate alias format
        if not _validate_key_alias(alias):
            return _response(400, {"error": "Invalid alias format. Use 1-50 alphanumeric characters, dashes, or underscores."})

        payload = {
            "user_id": user_id,
            "metadata": {"tier": tier, "email": email},
        }
        if alias:
            payload["key_alias"] = alias
        if limits["rpm_limit"]:
            payload["rpm_limit"] = limits["rpm_limit"]

        try:
            result = _litellm_request("POST", "/key/generate", payload)
        except Exception as e:
            return _response(400, {"error": "Invalid request"})
        return _response(200, {
            "token": result.get("token", ""),
            "key": result.get("key", ""),
            "key_alias": alias,
            "spend": 0,
            "max_budget": limits["max_budget"],
            "created_at": datetime.utcnow().isoformat(),
            "expires": None,
        })

    elif method == "GET" and path.rstrip("/") == "/api/keys":
        try:
            data = _litellm_request("GET", f"/key/list?user_id={user_id}&return_full_object=true")
        except Exception as e:
            return _response(500, {"error": "Internal server error"})
        keys = data if isinstance(data, list) else data.get("keys", [])
        result = []
        for k in keys:
            result.append({
                "token": k.get("token", ""),
                "key": k.get("key_name", k.get("token", "")[:8] + "..."),
                "key_alias": k.get("key_alias", ""),
                "spend": k.get("spend", 0),
                "max_budget": k.get("max_budget"),
                "created_at": k.get("created_at", ""),
                "expires": k.get("expires"),
            })
        return _response(200, result)

    elif method == "DELETE" and "/api/keys/" in path:
        token = path.split("/api/keys/")[-1]
        try:
            _litellm_request("POST", "/key/delete", {"keys": [token]})
        except Exception as e:
            return _response(400, {"error": "Invalid request"})
        return _response(200, {"deleted": True})

    return _response(404, {"error": "Not found"})
