import type { Metadata } from "next";
import DocsContent from "./DocsContent";

export const metadata: Metadata = {
  title: "API Documentation",
  description:
    "MiniMax-M2.5 API documentation. OpenAI-compatible endpoints, streaming, tool calling, and integration guides.",
};

export default function DocsPage() {
  return <DocsContent />;
}
