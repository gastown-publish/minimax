import type { Metadata } from "next";
import AuthProvider from "@/components/AuthProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "MiniMax-M2.5 API",
    template: "%s | MiniMax-M2.5 API",
  },
  description:
    "State-of-the-art open-source coding model API. 128K context, FP8 precision, OpenAI-compatible.",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
