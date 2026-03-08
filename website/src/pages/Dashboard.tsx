import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getStoredUser } from "../auth";
import {
  listKeys,
  createKey,
  deleteKey,
  getSubscription,
  getReferral,
  applyReferral,
  type ApiKey,
  type Subscription,
  type ReferralInfo,
} from "../api";
import { redirectToCheckout, TIERS } from "../stripe";
import KeyTable from "../components/KeyTable";
import PricingCard from "../components/PricingCard";
import {
  Key,
  Plus,
  Loader2,
  Copy,
  CreditCard,
  Gift,
  AlertCircle,
} from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [referral, setReferral] = useState<ReferralInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyAlias, setNewKeyAlias] = useState("");
  const [newKey, setNewKey] = useState<string | null>(null);
  const [referralCode, setReferralCode] = useState("");
  const [referralMsg, setReferralMsg] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"keys" | "billing" | "referral">("keys");

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [k, s, r] = await Promise.all([
        listKeys().catch(() => []),
        getSubscription().catch(() => null),
        getReferral().catch(() => null),
      ]);
      setKeys(k);
      setSubscription(s);
      setReferral(r);
    } catch {
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async () => {
    setCreating(true);
    setNewKey(null);
    try {
      const key = await createKey(newKeyAlias || undefined);
      setNewKey(key.key);
      setNewKeyAlias("");
      await loadData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteKey = async (token: string) => {
    if (!confirm("Delete this API key?")) return;
    try {
      await deleteKey(token);
      await loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleApplyReferral = async () => {
    try {
      const result = await applyReferral(referralCode);
      setReferralMsg(result.message);
      setReferralCode("");
      await loadData();
    } catch (err: any) {
      setReferralMsg(err.message);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-[var(--text-secondary)]">{user.email}</p>
        </div>
        {subscription && (
          <div className="text-right">
            <div className="text-sm">
              <span className="text-[var(--text-secondary)]">Plan: </span>
              <span className="font-semibold capitalize">{subscription.tier}</span>
            </div>
            <div className="text-sm text-[var(--text-secondary)]">
              ${subscription.spend.toFixed(2)} / ${subscription.budget.toFixed(2)} used
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-[var(--border)]">
        {[
          { id: "keys" as const, label: "API Keys", icon: Key },
          { id: "billing" as const, label: "Billing", icon: CreditCard },
          { id: "referral" as const, label: "Referrals", icon: Gift },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === id
                ? "border-sky-500 text-sky-400"
                : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 text-sm text-red-400 bg-red-600/10 border border-red-600/20 rounded-lg px-3 py-2">
          <AlertCircle size={16} />
          {error}
          <button onClick={() => setError("")} className="ml-auto text-red-400/50 hover:text-red-400">
            &times;
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={24} className="animate-spin text-sky-400" />
        </div>
      ) : (
        <>
          {/* API Keys Tab */}
          {tab === "keys" && (
            <div>
              {/* Create key form */}
              <div className="card mb-6">
                <h2 className="font-semibold mb-3">Create API Key</h2>
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={newKeyAlias}
                    onChange={(e) => setNewKeyAlias(e.target.value)}
                    placeholder="Key alias (optional)"
                    className="input-field max-w-xs"
                  />
                  <button
                    onClick={handleCreateKey}
                    disabled={creating}
                    className="btn-primary flex items-center gap-2"
                  >
                    {creating ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Plus size={16} />
                    )}
                    Create Key
                  </button>
                </div>

                {newKey && (
                  <div className="mt-4 bg-green-600/10 border border-green-600/20 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Key size={16} className="text-green-400" />
                      <span className="text-sm font-medium text-green-400">
                        Key created! Copy it now — it won't be shown again.
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-sm bg-[var(--bg-tertiary)] px-3 py-2 rounded font-mono">
                        {newKey}
                      </code>
                      <button
                        onClick={() => navigator.clipboard.writeText(newKey)}
                        className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                      >
                        <Copy size={16} />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Key list */}
              <div className="card">
                <h2 className="font-semibold mb-3">
                  Your Keys ({keys.length}
                  {subscription ? ` / ${subscription.max_keys === -1 ? "∞" : subscription.max_keys}` : ""})
                </h2>
                <KeyTable keys={keys} onDelete={handleDeleteKey} />
              </div>
            </div>
          )}

          {/* Billing Tab */}
          {tab === "billing" && (
            <div>
              {subscription && (
                <div className="card mb-6">
                  <h2 className="font-semibold mb-4">Current Plan</h2>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                      <div className="text-xs text-[var(--text-secondary)] uppercase">Plan</div>
                      <div className="text-lg font-bold capitalize">{subscription.tier}</div>
                    </div>
                    <div>
                      <div className="text-xs text-[var(--text-secondary)] uppercase">Budget</div>
                      <div className="text-lg font-bold">${subscription.budget}</div>
                    </div>
                    <div>
                      <div className="text-xs text-[var(--text-secondary)] uppercase">Spend</div>
                      <div className="text-lg font-bold">${subscription.spend.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-[var(--text-secondary)] uppercase">RPM</div>
                      <div className="text-lg font-bold">
                        {subscription.rpm === -1 ? "Unlimited" : subscription.rpm}
                      </div>
                    </div>
                  </div>
                  {/* Usage bar */}
                  <div className="mt-4">
                    <div className="flex justify-between text-xs text-[var(--text-secondary)] mb-1">
                      <span>Budget usage</span>
                      <span>
                        {((subscription.spend / subscription.budget) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sky-500 rounded-full transition-all"
                        style={{
                          width: `${Math.min((subscription.spend / subscription.budget) * 100, 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <h2 className="font-semibold mb-4">Upgrade Plan</h2>
              <div className="grid md:grid-cols-3 gap-6">
                {TIERS.map((tier) => (
                  <PricingCard
                    key={tier.id}
                    {...tier}
                    currentTier={subscription?.tier}
                    onSelect={() => {
                      if (tier.id !== "free") {
                        redirectToCheckout(tier.id);
                      }
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Referrals Tab */}
          {tab === "referral" && (
            <div className="max-w-lg">
              {referral && (
                <div className="card mb-6">
                  <h2 className="font-semibold mb-3">Your Referral Code</h2>
                  <p className="text-sm text-[var(--text-secondary)] mb-3">
                    Share your code. You get $5 credit, they get 1 month free Pro.
                  </p>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-lg bg-[var(--bg-tertiary)] px-4 py-3 rounded-lg font-mono text-center">
                      {referral.code}
                    </code>
                    <button
                      onClick={() => navigator.clipboard.writeText(referral.code)}
                      className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <div className="text-xs text-[var(--text-secondary)]">Referrals</div>
                      <div className="text-lg font-bold">{referral.referral_count}</div>
                    </div>
                    <div>
                      <div className="text-xs text-[var(--text-secondary)]">Credit earned</div>
                      <div className="text-lg font-bold">${referral.credit_earned.toFixed(2)}</div>
                    </div>
                  </div>
                </div>
              )}

              <div className="card">
                <h2 className="font-semibold mb-3">Apply a Referral Code</h2>
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={referralCode}
                    onChange={(e) => setReferralCode(e.target.value)}
                    placeholder="Enter referral code"
                    className="input-field"
                  />
                  <button
                    onClick={handleApplyReferral}
                    disabled={!referralCode.trim()}
                    className="btn-primary whitespace-nowrap"
                  >
                    Apply
                  </button>
                </div>
                {referralMsg && (
                  <p className="text-sm mt-3 text-[var(--text-secondary)]">{referralMsg}</p>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
