import { createCheckout } from "./api";

export type BillingPeriod = "monthly" | "yearly";

export async function redirectToCheckout(
  tier: string,
  billingPeriod: BillingPeriod = "monthly",
  promoCode?: string,
): Promise<void> {
  const { url } = await createCheckout(tier, billingPeriod, promoCode);
  window.location.href = url;
}

export interface Tier {
  id: string;
  name: string;
  price: string;
  yearlyPrice: string;
  yearlyTotal: string;
  period: string;
  budget: string;
  rpm: string;
  keys: string;
  features: readonly string[];
  cta: string;
  popular: boolean;
}

export const TIERS: Tier[] = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    yearlyPrice: "$0",
    yearlyTotal: "$0",
    period: "/mo",
    budget: "$5",
    rpm: "5",
    keys: "5",
    features: [
      "$5/month API budget",
      "5 requests per minute",
      "5 API keys",
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
    yearlyPrice: "$16",
    yearlyTotal: "$192",
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
    yearlyPrice: "$80",
    yearlyTotal: "$960",
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
];
