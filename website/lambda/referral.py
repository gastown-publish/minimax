"""Lambda function for referral system.

Endpoints:
  GET  /api/referral       — Get user's referral code + stats
  POST /api/referral/apply — Apply a referral code (credit both parties)
"""

import json
import os
import secrets
import string
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
users_table = dynamodb.Table("minimax-users")

REFERRER_CREDIT = Decimal("5.00")  # $5 credit for referrer
REFEREE_FREE_MONTHS = 1  # 1 month free Pro for referee


def _generate_code():
    """Generate a short referral code like 'MINI-ABCD'."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(4))
    return f"MINI-{suffix}"


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
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }
    origin = _cors_origin(event) if event else None
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(body, default=str),
    }


def _get_or_create_user(user_id, email=""):
    """Get user record, creating with default values if needed."""
    resp = users_table.get_item(Key={"user_id": user_id})
    item = resp.get("Item")

    if not item:
        item = {
            "user_id": user_id,
            "email": email,
            "tier": "free",
            "referral_code": _generate_code(),
            "referral_count": 0,
            "credit_earned": Decimal("0"),
            "referred_by": None,
        }
        users_table.put_item(Item=item)

    return item


def handler(event, context):
    method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method"))
    path = event.get("path", event.get("rawPath", ""))

    if method == "OPTIONS":
        return _response(200, {}, event)

    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
    )
    user_id = claims.get("sub", "")
    email = claims.get("email", "")

    if not user_id:
        return _response(401, {"error": "Unauthorized"}, event)

    user = _get_or_create_user(user_id, email)

    if method == "GET" and path.rstrip("/") == "/api/referral":
        return _response(200, {
            "code": user.get("referral_code", ""),
            "referral_count": int(user.get("referral_count", 0)),
            "credit_earned": float(user.get("credit_earned", 0)),
        }, event)

    elif method == "POST" and path.rstrip("/") == "/api/referral/apply":
        body = json.loads(event.get("body", "{}") or "{}")
        code = body.get("code", "").strip().upper()

        if not code:
            return _response(400, {"error": "Referral code is required"}, event)

        # Can't use own code
        if code == user.get("referral_code"):
            return _response(400, {"error": "Cannot use your own referral code"}, event)

        # Already referred
        if user.get("referred_by"):
            return _response(400, {"error": "You have already used a referral code"}, event)

        # Find referrer by scanning for referral_code
        # Note: In production, use a GSI on referral_code
        scan_resp = users_table.scan(
            FilterExpression="referral_code = :code",
            ExpressionAttributeValues={":code": code},
            Limit=1,
        )
        items = scan_resp.get("Items", [])
        if not items:
            return _response(400, {"error": "Invalid referral code"}, event)

        referrer = items[0]
        referrer_id = referrer["user_id"]

        # Update referee
        users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET referred_by = :ref",
            ExpressionAttributeValues={":ref": referrer_id},
        )

        # Credit referrer
        users_table.update_item(
            Key={"user_id": referrer_id},
            UpdateExpression="SET referral_count = referral_count + :one, credit_earned = credit_earned + :credit",
            ExpressionAttributeValues={
                ":one": 1,
                ":credit": REFERRER_CREDIT,
            },
        )

        return _response(200, {
            "message": f"Referral applied! You get {REFEREE_FREE_MONTHS} month(s) free Pro.",
        }, event)

    return _response(404, {"error": "Not found"}, event)
