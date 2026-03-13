import { getIdToken, refreshSession } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://api.minimax.villamarket.ai";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getIdToken();
  const resp = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  // Auto-refresh expired tokens and retry
  if (resp.status === 401 && token) {
    const refreshed = await refreshSession();
    if (refreshed) {
      const newToken = getIdToken();
      const retry = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...(newToken ? { Authorization: `Bearer ${newToken}` } : {}),
          ...options.headers,
        },
      });
      if (!retry.ok) {
        const body = await retry.json().catch(() => ({}));
        throw new Error(body.error || body.message || `API error ${retry.status}`);
      }
      return retry.json();
    }
  }

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error || body.message || `API error ${resp.status}`);
  }

  return resp.json();
}

// ── API Keys ────────────────────────────────────────────────────────

export interface ApiKey {
  token: string;
  key: string;
  key_alias: string;
  spend: number;
  max_budget: number | null;
  created_at: string;
  expires: string | null;
}

export async function listKeys(): Promise<ApiKey[]> {
  return apiFetch<ApiKey[]>("/api/keys");
}

export async function createKey(alias?: string): Promise<ApiKey> {
  return apiFetch<ApiKey>("/api/keys", {
    method: "POST",
    body: JSON.stringify({ alias }),
  });
}

export async function deleteKey(token: string): Promise<void> {
  await apiFetch(`/api/keys/${token}`, { method: "DELETE" });
}

// ── Stripe ──────────────────────────────────────────────────────────

export interface CheckoutResponse {
  url: string;
  sessionId: string;
}

export async function createCheckout(
  tier: string,
  billingPeriod: "monthly" | "yearly" = "monthly",
  promoCode?: string,
): Promise<CheckoutResponse> {
  return apiFetch<CheckoutResponse>("/api/checkout", {
    method: "POST",
    body: JSON.stringify({ tier, billing_period: billingPeriod, promo_code: promoCode }),
  });
}

// ── Subscription ────────────────────────────────────────────────────

export interface Subscription {
  tier: "free" | "pro" | "enterprise";
  status: string;
  budget: number;
  spend: number;
  rpm: number;
  max_keys: number;
  current_period_end: string | null;
}

export async function getSubscription(): Promise<Subscription> {
  return apiFetch<Subscription>("/api/subscription");
}

// ── Promo Codes ─────────────────────────────────────────────────────

export interface PromoResult {
  valid: boolean;
  discount_pct?: number;
  free_months?: number;
  message?: string;
}

export async function validatePromo(code: string): Promise<PromoResult> {
  return apiFetch<PromoResult>("/api/promo/validate", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

// ── Referrals ───────────────────────────────────────────────────────

export interface ReferralInfo {
  code: string;
  referral_count: number;
  credit_earned: number;
}

export async function getReferral(): Promise<ReferralInfo> {
  return apiFetch<ReferralInfo>("/api/referral");
}

export async function applyReferral(code: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/api/referral/apply", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

// ── Usage ───────────────────────────────────────────────────────────

export interface UsageData {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  daily: Array<{
    date: string;
    requests: number;
    tokens: number;
    cost: number;
  }>;
}

export async function getUsage(days?: number): Promise<UsageData> {
  const params = days ? `?days=${days}` : "";
  return apiFetch<UsageData>(`/api/usage${params}`);
}
