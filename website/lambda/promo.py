"""Lambda function for promo code validation.

Endpoint: POST /api/promo/validate
"""

import json
import os
from datetime import datetime
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
promos_table = dynamodb.Table("minimax-promos")

_ALLOWED_ORIGINS = {
    "https://minimax.villamarket.ai",
    "https://app.minimax.villamarket.ai",
    "http://localhost:3000",
}


def _cors_origin(event):
    """Return the request origin if it is in the allowed whitelist, or None."""
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin") or ""
    return origin if origin in _ALLOWED_ORIGINS else None


def _response(status, body, event=None):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }
    origin = _cors_origin(event) if event else None
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(body, default=str),
    }


def handler(event, context):
    method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method"))

    if method == "OPTIONS":
        return _response(200, {}, event)

    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
    )
    if not claims.get("sub"):
        return _response(401, {"error": "Unauthorized"}, event)

    body = json.loads(event.get("body", "{}") or "{}")
    code = body.get("code", "").strip().upper()

    if not code:
        return _response(400, {"error": "Code is required"}, event)

    try:
        resp = promos_table.get_item(Key={"code": code})
    except Exception as e:
        return _response(500, {"error": str(e)}, event)

    item = resp.get("Item")
    if not item:
        return _response(200, {"valid": False, "message": "Invalid promo code"}, event)

    # Check expiration
    expires_at = item.get("expires_at")
    if expires_at and datetime.fromisoformat(str(expires_at)) < datetime.utcnow():
        return _response(200, {"valid": False, "message": "Promo code has expired"}, event)

    # Check usage limit
    max_uses = int(item.get("max_uses", 0))
    uses = int(item.get("uses", 0))
    if max_uses > 0 and uses >= max_uses:
        return _response(200, {"valid": False, "message": "Promo code has reached its usage limit"}, event)

    return _response(200, {
        "valid": True,
        "discount_pct": int(item.get("discount_pct", 0)),
        "free_months": int(item.get("free_months", 0)),
        "message": f"Code {code} applied!",
    }, event)
