import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { AI_TOOLS } from "@/lib/tools";

export const metadata: Metadata = {
  title: "AI Document Tools",
  description: "Chat with your PDFs, summarize, generate study notes, MCQs, and more — grounded in your actual documents.",
};

export default function AIPage() {
  return (
    <div className="mx-auto max-w-5xl px-5 py-16">
      <p className="mb-3 flex items-center gap-1.5 text-[13px] font-medium uppercase tracking-wide text-stamp">
        <Sparkles size={14} /> AI Document Assistant
      </p>
      <h1 className="font-display text-4xl font-medium tracking-tight text-ink">Your Documents, Now Intelligent.</h1>
      <p className="mt-3 max-w-xl text-[16px] text-ink-soft">
        Upload a document and let AI summarize, explain, analyze and answer questions about it — using a proper
        retrieval pipeline grounded in the document&apos;s actual pages, with citations, and never confident
        fabrication.
      </p>

      <div className="mt-6 rounded-lg border border-line bg-paper-raised p-4 text-[14px] text-ink-soft">
        These AI tools require an LLM provider key (OpenAI, Gemini, or Groq) configured on the backend — see{" "}
        <code className="rounded bg-paper px-1.5 py-0.5 text-[13px]">.env.example</code>. The retrieval pipeline
        (chunking, embeddings, vector search, citation-grounded answers) is scaffolded in{" "}
        <code className="rounded bg-paper px-1.5 py-0.5 text-[13px]">backend/app/services/ai/</code> and activates
        once a key is set.
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {AI_TOOLS.map((tool) => (
          <Link
            key={tool.slug}
            href={`/ai/${tool.slug}`}
            className="group rounded-lg border border-line bg-paper-raised p-5 transition hover:border-stamp"
          >
            <p className="font-display text-lg text-ink">{tool.name}</p>
            <p className="mt-1.5 text-[14px] text-ink-soft">{tool.description}</p>
            <ArrowRight size={15} className="mt-4 text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-stamp" />
          </Link>
        ))}
      </div>
    </div>
  );
}
