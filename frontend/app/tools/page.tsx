import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { TOOLS, ToolCategory } from "@/lib/tools";

export const metadata: Metadata = {
  title: "All Tools",
  description: "Every PDF and document tool in DocuConvert AI, in one place.",
};

const CATEGORIES: ToolCategory[] = ["Convert", "Organize", "Edit", "Security"];

export default function ToolsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-16">
      <div className="max-w-xl">
        <h1 className="font-display text-4xl font-medium tracking-tight text-ink">All Tools</h1>
        <p className="mt-3 text-[16px] text-ink-soft">
          Every conversion, organization, editing, and security tool — free to start, no install required.
        </p>
      </div>

      {CATEGORIES.map((cat) => {
        const items = TOOLS.filter((t) => t.category === cat);
        if (!items.length) return null;
        return (
          <section key={cat} className="mt-12">
            <h2 className="mb-4 border-b border-line pb-3 font-display text-xl text-ink">{cat}</h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/tools/${tool.slug}`}
                  className="group flex items-center justify-between rounded-lg border border-line bg-paper-raised px-4 py-3.5 transition hover:border-stamp"
                >
                  <div>
                    <p className="text-[15px] font-medium text-ink">{tool.name}</p>
                    <p className="mt-0.5 text-[13px] text-ink-faint">{tool.short}</p>
                  </div>
                  <ArrowRight size={16} className="shrink-0 text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-stamp" />
                </Link>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
