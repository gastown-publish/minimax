"use client";

import { Check } from "lucide-react";
import type { Tier, BillingPeriod } from "@/lib/stripe";

interface PricingCardProps {
  tier: Tier;
  billingPeriod: BillingPeriod;
  currentTier?: string;
  onSelect: () => void;
}

export default function PricingCard({
  tier,
  billingPeriod,
  currentTier,
  onSelect,
}: PricingCardProps) {
  const isCurrent = currentTier === tier.name.toLowerCase();
  const isYearly = billingPeriod === "yearly";
  const displayPrice = isYearly ? tier.yearlyPrice : tier.price;
  const showSavings = isYearly && tier.id !== "free" && tier.price !== tier.yearlyPrice;

  return (
    <div
      className={`card relative flex flex-col ${
        tier.popular
          ? "border-sky-500/50 ring-1 ring-sky-500/20"
          : ""
      }`}
    >
      {tier.popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-sky-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
          Most Popular
        </div>
      )}

      <h3 className="text-lg font-semibold">{tier.name}</h3>
      <div className="mt-3 mb-1">
        <span className="text-4xl font-bold">{displayPrice}</span>
        <span className="text-[var(--text-secondary)]">/mo</span>
      </div>
      {isYearly && tier.id !== "free" ? (
        <div className="mb-6 text-sm">
          <span className="text-[var(--text-secondary)] line-through mr-2">{tier.price}/mo</span>
          <span className="text-emerald-400 font-medium">billed {tier.yearlyTotal}/yr</span>
        </div>
      ) : (
        <div className="mb-6" />
      )}

      {showSavings && (
        <div className="absolute top-4 right-4 bg-emerald-600/20 text-emerald-400 text-xs font-semibold px-2 py-0.5 rounded-full border border-emerald-600/30">
          Save 20%
        </div>
      )}

      <ul className="space-y-3 mb-8 flex-1">
        {tier.features.map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm">
            <Check size={16} className="text-sky-400 mt-0.5 flex-shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onSelect}
        disabled={isCurrent}
        className={`w-full py-2.5 rounded-lg font-medium transition-colors ${
          isCurrent
            ? "bg-green-600/20 text-green-400 border border-green-600/30 cursor-default"
            : tier.popular
            ? "bg-sky-600 hover:bg-sky-500 text-white"
            : "bg-[var(--bg-tertiary)] hover:bg-[#252525] text-[var(--text-primary)] border border-[var(--border)]"
        }`}
      >
        {isCurrent ? "Current Plan" : tier.cta}
      </button>
    </div>
  );
}
