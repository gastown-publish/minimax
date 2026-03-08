import { Check } from "lucide-react";

interface PricingCardProps {
  name: string;
  price: string;
  period: string;
  budget: string;
  rpm: string;
  keys: string;
  features: readonly string[];
  cta: string;
  popular: boolean;
  currentTier?: string;
  onSelect: () => void;
}

export default function PricingCard({
  name,
  price,
  period,
  features,
  cta,
  popular,
  currentTier,
  onSelect,
}: PricingCardProps) {
  const isCurrent = currentTier === name.toLowerCase();

  return (
    <div
      className={`card relative flex flex-col ${
        popular
          ? "border-sky-500/50 ring-1 ring-sky-500/20"
          : ""
      }`}
    >
      {popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-sky-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
          Most Popular
        </div>
      )}

      <h3 className="text-lg font-semibold">{name}</h3>
      <div className="mt-3 mb-6">
        <span className="text-4xl font-bold">{price}</span>
        <span className="text-[var(--text-secondary)]">{period}</span>
      </div>

      <ul className="space-y-3 mb-8 flex-1">
        {features.map((feature) => (
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
            : popular
            ? "bg-sky-600 hover:bg-sky-500 text-white"
            : "bg-[var(--bg-tertiary)] hover:bg-[#252525] text-[var(--text-primary)] border border-[var(--border)]"
        }`}
      >
        {isCurrent ? "Current Plan" : cta}
      </button>
    </div>
  );
}
