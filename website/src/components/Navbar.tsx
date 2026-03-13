"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { Menu, X, LogOut } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleSignOut = async () => {
    await logout();
    router.push("/");
  };

  const links: { href: string; label: string; external?: boolean }[] = [
    { href: "/", label: "Home" },
    { href: "/docs", label: "Docs" },
    ...(user
      ? [
          { href: "/dashboard", label: "Dashboard" },
          { href: "/tools", label: "Tools" },
          { href: "https://app.minimax.villamarket.ai", label: "Chat", external: true },
        ]
      : []),
  ];

  return (
    <nav className="border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <span className="text-sky-400">M</span>
            <span>MiniMax-M2.5</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            {links.map((link) =>
              link.external ? (
                <a
                  key={link.href}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm transition-colors text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-sm transition-colors ${
                    pathname === link.href
                      ? "text-sky-400"
                      : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  {link.label}
                </Link>
              )
            )}
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-xs text-[var(--text-secondary)]">
                  {user.email}
                </span>
                <button
                  onClick={handleSignOut}
                  className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                  title="Sign out"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <Link href="/login" className="btn-primary text-sm">
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden text-[var(--text-secondary)]"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-[var(--border)] bg-[var(--bg-primary)]">
          <div className="px-4 py-3 space-y-2">
            {links.map((link) =>
              link.external ? (
                <a
                  key={link.href}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setMobileOpen(false)}
                  className="block py-2 text-sm text-[var(--text-secondary)]"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={`block py-2 text-sm ${
                    pathname === link.href
                      ? "text-sky-400"
                      : "text-[var(--text-secondary)]"
                  }`}
                >
                  {link.label}
                </Link>
              )
            )}
            {user ? (
              <button
                onClick={handleSignOut}
                className="block py-2 text-sm text-red-400"
              >
                Sign Out
              </button>
            ) : (
              <Link
                href="/login"
                onClick={() => setMobileOpen(false)}
                className="block py-2 text-sm text-sky-400"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
