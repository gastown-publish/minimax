"""Lambda function for Stripe checkout session creation.

Endpoint: POST /api/checkout
"""

import json
import os

import stripe

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

PRICE_IDS = {
    "pro": {
        "monthly": os.environ.get("STRIPE_PRICE_PRO", ""),
        "yearly": os.environ.get("STRIPE_PRICE_PRO_YEARLY", ""),
    },
    "enterprise": {
        "monthly": os.environ.get("STRIPE_PRICE_ENTERPRISE", ""),
        "yearly": os.environ.get("STRIPE_PRICE_ENTERPRISE_YEARLY", ""),
    },
}

SITE_URL = os.environ.get("SITE_URL", "https://minimax.villamarket.ai")


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body),
    }


def handler(event, context):
    method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method"))

    if method == "OPTIONS":
        return _response(200, {})

    # HTTP API v2.0 payload: claims at authorizer.jwt.claims
    # REST API v1.0 payload: claims at authorizer.claims
    authorizer = event.get("requestContext", {}).get("authorizer", {})
    claims = authorizer.get("jwt", {}).get("claims", {}) or authorizer.get("claims", {})
    user_id = claims.get("sub", "")
    email = claims.get("email", "")

    if not user_id:
        return _response(401, {"error": "Unauthorized"})

    body = json.loads(event.get("body", "{}") or "{}")
    tier = body.get("tier", "")
    billing_period = body.get("billing_period", "monthly")
    promo_code = body.get("promo_code")

    if tier not in PRICE_IDS:
        return _response(400, {"error": f"Invalid tier: {tier}"})

    if billing_period not in ("monthly", "yearly"):
        return _response(400, {"error": f"Invalid billing_period: {billing_period}"})

    price_id = PRICE_IDS[tier].get(billing_period, "")
    if not price_id:
        return _response(400, {"error": f"No price configured for {tier}/{billing_period}"})

    checkout_params = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{SITE_URL}/dashboard?checkout=success",
        "cancel_url": f"{SITE_URL}/dashboard?checkout=cancel",
        "customer_email": email,
        "client_reference_id": user_id,
        "metadata": {"user_id": user_id, "tier": tier, "billing_period": billing_period},
    }

    if promo_code:
        checkout_params["allow_promotion_codes"] = True

    session = stripe.checkout.Session.create(**checkout_params)

    return _response(200, {
        "url": session.url,
        "sessionId": session.id,
    })
