"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-[var(--border)] py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between text-sm text-[var(--text-secondary)]">
        <span>MiniMax-M2.5 API by villamarket.ai</span>
        <div className="flex gap-4">
          <Link href="/docs" className="hover:text-[var(--text-primary)]">
            Docs
          </Link>
          <a
            href="https://huggingface.co/MiniMaxAI/MiniMax-M2.5"
            target="_blank"
            rel="noopener"
            className="hover:text-[var(--text-primary)]"
          >
            Model
          </a>
        </div>
      </div>
    </footer>
  );
}
