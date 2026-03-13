"use client";

import type { BillingPeriod } from "@/lib/stripe";

interface PricingToggleProps {
  value: BillingPeriod;
  onChange: (period: BillingPeriod) => void;
}

export default function PricingToggle({ value, onChange }: PricingToggleProps) {
  return (
    <div className="flex items-center justify-center gap-1">
      <div className="inline-flex items-center bg-[var(--bg-tertiary)] border border-[var(--border)] rounded-full p-1">
        <button
          onClick={() => onChange("monthly")}
          className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${
            value === "monthly"
              ? "bg-sky-600 text-white"
              : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          Monthly
        </button>
        <button
          onClick={() => onChange("yearly")}
          className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${
            value === "yearly"
              ? "bg-sky-600 text-white"
              : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          Yearly
          <span className="ml-1.5 text-xs text-emerald-400 font-semibold">Save 20%</span>
        </button>
      </div>
    </div>
  );
}
