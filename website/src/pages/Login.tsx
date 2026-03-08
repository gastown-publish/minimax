import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  signIn,
  signUp,
  confirmSignUp,
  signInWithGoogle,
  signInWithApple,
  exchangeCode,
  getStoredUser,
} from "../auth";
import { Mail, Lock, ArrowRight, Loader2 } from "lucide-react";

type AuthMode = "signin" | "signup" | "confirm";

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<AuthMode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (getStoredUser()) {
      navigate("/dashboard");
    }
  }, [navigate]);

  // Handle OAuth callback
  useEffect(() => {
    const authCode = searchParams.get("code");
    if (authCode) {
      setLoading(true);
      exchangeCode(authCode)
        .then(() => navigate("/dashboard"))
        .catch((e) => {
          setError(e.message);
          setLoading(false);
        });
    }
  }, [searchParams, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "signup") {
        await signUp(email, password);
        setMode("confirm");
      } else if (mode === "confirm") {
        await confirmSignUp(email, code);
        await signIn(email, password);
        navigate("/dashboard");
      } else {
        await signIn(email, password);
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-56px)] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold mb-2">
            {mode === "signin"
              ? "Sign in"
              : mode === "signup"
              ? "Create account"
              : "Verify email"}
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            {mode === "confirm"
              ? `We sent a code to ${email}`
              : "Access the MiniMax-M2.5 API"}
          </p>
        </div>

        {/* Social login */}
        {mode !== "confirm" && (
          <>
            <div className="space-y-3 mb-6">
              <button
                onClick={signInWithGoogle}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 py-2.5 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                <svg viewBox="0 0 24 24" width="18" height="18">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Continue with Google
              </button>

              <button
                onClick={signInWithApple}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 py-2.5 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="black">
                  <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
                </svg>
                Continue with Apple
              </button>
            </div>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[var(--border)]" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[var(--bg-primary)] px-3 text-[var(--text-secondary)]">
                  or continue with email
                </span>
              </div>
            </div>
          </>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode !== "confirm" && (
            <>
              <div className="relative">
                <Mail
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]"
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email address"
                  required
                  className="input-field pl-10"
                />
              </div>
              <div className="relative">
                <Lock
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]"
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  required
                  minLength={8}
                  className="input-field pl-10"
                />
              </div>
            </>
          )}

          {mode === "confirm" && (
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Verification code"
              required
              className="input-field text-center text-2xl tracking-widest"
              maxLength={6}
            />
          )}

          {error && (
            <div className="text-sm text-red-400 bg-red-600/10 border border-red-600/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <>
                {mode === "signin"
                  ? "Sign In"
                  : mode === "signup"
                  ? "Create Account"
                  : "Verify"}
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        {mode !== "confirm" && (
          <p className="text-center text-sm text-[var(--text-secondary)] mt-6">
            {mode === "signin" ? (
              <>
                Don't have an account?{" "}
                <button
                  onClick={() => {
                    setMode("signup");
                    setError("");
                  }}
                  className="text-sky-400 hover:underline"
                >
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  onClick={() => {
                    setMode("signin");
                    setError("");
                  }}
                  className="text-sky-400 hover:underline"
                >
                  Sign in
                </button>
              </>
            )}
          </p>
        )}
      </div>
    </div>
  );
}
