"""Lambda function for Stripe webhook events.

Endpoint: POST /api/stripe-webhook
Handles: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted
"""

import json
import os

import boto3
import stripe

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
users_table = dynamodb.Table("minimax-users")

# Map all price IDs (monthly + yearly) to tiers
TIER_MAP = {
    os.environ.get("STRIPE_PRICE_PRO", ""): "pro",
    os.environ.get("STRIPE_PRICE_PRO_YEARLY", ""): "pro",
    os.environ.get("STRIPE_PRICE_ENTERPRISE", ""): "enterprise",
    os.environ.get("STRIPE_PRICE_ENTERPRISE_YEARLY", ""): "enterprise",
}


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _update_user_tier(user_id, tier, stripe_customer_id=None, subscription_id=None):
    """Update user tier in DynamoDB."""
    update_expr = "SET tier = :tier"
    expr_values = {":tier": tier}

    if stripe_customer_id:
        update_expr += ", stripe_customer_id = :cid"
        expr_values[":cid"] = stripe_customer_id

    if subscription_id:
        update_expr += ", subscription_id = :sid"
        expr_values[":sid"] = subscription_id

    users_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
    )


def handler(event, context):
    body = event.get("body", "")
    sig_header = event.get("headers", {}).get("stripe-signature", "")

    try:
        evt = stripe.Webhook.construct_event(body, sig_header, WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return _response(400, {"error": str(e)})

    event_type = evt["type"]
    data = evt["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("client_reference_id") or data.get("metadata", {}).get("user_id")
        tier = data.get("metadata", {}).get("tier", "pro")
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")

        if user_id:
            _update_user_tier(user_id, tier, customer_id, subscription_id)

    elif event_type == "customer.subscription.updated":
        subscription = data
        customer_id = subscription.get("customer")

        # Find user by stripe_customer_id
        # Note: In production, you'd query by GSI on stripe_customer_id
        price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
        new_tier = TIER_MAP.get(price_id, "pro")

        # If subscription is active, update tier
        if subscription.get("status") == "active":
            metadata = subscription.get("metadata", {})
            user_id = metadata.get("user_id")
            if user_id:
                _update_user_tier(user_id, new_tier)

    elif event_type == "customer.subscription.deleted":
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        if user_id:
            _update_user_tier(user_id, "free")

    return _response(200, {"received": True})
