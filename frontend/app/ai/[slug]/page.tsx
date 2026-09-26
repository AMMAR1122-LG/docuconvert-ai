import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { AI_TOOLS } from "@/lib/tools";

export function generateStaticParams() {
  return AI_TOOLS.map((t) => ({ slug: t.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const tool = AI_TOOLS.find((t) => t.slug === slug);
  if (!tool) return {};
  return { title: tool.name, description: tool.description };
}

export default async function AIToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const tool = AI_TOOLS.find((t) => t.slug === slug);
  if (!tool) notFound();

  return (
    <div className="mx-auto max-w-2xl px-5 py-16">
      <h1 className="font-display text-3xl font-medium tracking-tight text-ink">{tool.name}</h1>
      <p className="mt-3 text-[16px] text-ink-soft">{tool.description}</p>

      <div className="mt-10 rounded-xl border border-dashed border-line-strong bg-paper-raised p-8 text-center">
        <p className="font-display text-lg text-ink">Needs an AI provider key</p>
        <p className="mx-auto mt-2 max-w-sm text-[14px] text-ink-soft">
          This tool calls the RAG pipeline in <code className="rounded bg-paper px-1 py-0.5">backend/app/services/ai/</code> —
          set <code className="rounded bg-paper px-1 py-0.5">OPENAI_API_KEY</code>,{" "}
          <code className="rounded bg-paper px-1 py-0.5">GEMINI_API_KEY</code>, or{" "}
          <code className="rounded bg-paper px-1 py-0.5">GROQ_API_KEY</code> to activate it.
        </p>
      </div>

      <div className="mt-10 text-left">
        <h2 className="font-display text-lg text-ink">How it works under the hood</h2>
        <ol className="mt-3 space-y-2 text-[14px] text-ink-soft">
          <li>1. Your document&apos;s text is extracted and split into overlapping chunks.</li>
          <li>2. Each chunk is embedded and stored in the vector index for this document.</li>
          <li>3. Your question retrieves the most relevant chunks.</li>
          <li>4. The model answers using only those chunks, citing the source page.</li>
        </ol>
      </div>
    </div>
  );
}
