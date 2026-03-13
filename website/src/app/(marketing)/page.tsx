import type { Metadata } from "next";
import LandingContent from "./LandingContent";

export const metadata: Metadata = {
  title: "MiniMax-M2.5 API — Open Source Coding Model",
  description:
    "State-of-the-art coding model API. 80.2% SWE-Bench Verified. 128K context, FP8 precision, 8x H100 GPUs. OpenAI-compatible.",
};

export default function LandingPage() {
  return <LandingContent />;
}
