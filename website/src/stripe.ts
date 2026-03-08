import { createCheckout } from "./api";

export async function redirectToCheckout(tier: string, promoCode?: string): Promise<void> {
  const { url } = await createCheckout(tier, promoCode);
  // Stripe checkout sessions return a URL — redirect to it
  window.location.href = url;
}

export const TIERS = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    period: "/mo",
    budget: "$1",
    rpm: "5",
    keys: "1",
    features: [
      "$1/month API budget",
      "5 requests per minute",
      "1 API key",
      "128K context",
      "Community support",
    ],
    cta: "Get Started",
    popular: false,
  },
  {
    id: "pro",
    name: "Pro",
    price: "$20",
    period: "/mo",
    budget: "$20",
    rpm: "16",
    keys: "5",
    features: [
      "$20/month API budget",
      "16 requests per minute",
      "5 API keys",
      "128K context",
      "Priority support",
      "Usage analytics",
    ],
    cta: "Upgrade to Pro",
    popular: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "$100",
    period: "/mo",
    budget: "$100",
    rpm: "Unlimited",
    keys: "Unlimited",
    features: [
      "$100/month API budget",
      "Unlimited requests per minute",
      "Unlimited API keys",
      "128K context",
      "Dedicated support",
      "Usage analytics",
      "Custom integrations",
    ],
    cta: "Go Enterprise",
    popular: false,
  },
] as const;
