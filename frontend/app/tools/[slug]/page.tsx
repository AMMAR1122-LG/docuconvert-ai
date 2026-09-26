import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTool, TOOLS } from "@/lib/tools";
import { TOOL_CONFIGS } from "@/lib/toolConfigs";
import { UploadTool } from "@/components/UploadTool";

export function generateStaticParams() {
  return TOOLS.map((t) => ({ slug: t.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const tool = getTool(slug);
  if (!tool) return {};
  return {
    title: `${tool.name} Online — Free`,
    description: tool.description,
    alternates: { canonical: `/tools/${tool.slug}` },
  };
}

const FAQS: Record<string, { q: string; a: string }[]> = {
  default: [
    { q: "Is this free?", a: "Yes — free-plan use covers everyday file sizes and daily volume. Pro removes the limits." },
    { q: "Are my documents secure?", a: "Files are transferred over HTTPS, processed, and then automatically deleted after a short retention window." },
    { q: "How large can my file be?", a: "10MB on the free plan, 100MB on Pro." },
  ],
};

export default async function ToolPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const tool = getTool(slug);
  if (!tool) notFound();

  const config = TOOL_CONFIGS[slug];
  const related = TOOLS.filter((t) => t.category === tool.category && t.slug !== tool.slug).slice(0, 4);
  const faqs = FAQS[slug] || FAQS.default;

  return (
    <div className="mx-auto max-w-6xl px-5 py-14">
      <div className="mx-auto max-w-2xl text-center">
        <p className="mb-2 text-[13px] font-medium uppercase tracking-wide text-stamp">{tool.category}</p>
        <h1 className="font-display text-3xl font-medium tracking-tight text-ink sm:text-4xl">{tool.name} Online</h1>
        <p className="mt-3 text-[16px] text-ink-soft">{tool.description}</p>
      </div>

      <div className="mt-10">
        {config ? (
          <UploadTool config={config} />
        ) : (
          <div className="mx-auto max-w-md rounded-xl border border-dashed border-line-strong bg-paper-raised p-8 text-center">
            <p className="font-display text-lg text-ink">Coming soon</p>
            <p className="mt-2 text-[14px] text-ink-soft">
              {tool.name} isn&apos;t wired up in this build yet — it follows the same upload → process → download
              pattern as the other tools once implemented.
            </p>
          </div>
        )}
      </div>

      <div className="mx-auto mt-20 grid max-w-3xl gap-10 sm:grid-cols-3">
        <div>
          <h2 className="font-display text-lg text-ink">1. Upload</h2>
          <p className="mt-1.5 text-[14px] text-ink-soft">Select or drag in your file.</p>
        </div>
        <div>
          <h2 className="font-display text-lg text-ink">2. Process</h2>
          <p className="mt-1.5 text-[14px] text-ink-soft">Our system handles the conversion on the server.</p>
        </div>
        <div>
          <h2 className="font-display text-lg text-ink">3. Download</h2>
          <p className="mt-1.5 text-[14px] text-ink-soft">Get your result immediately — nothing is stored longer than needed.</p>
        </div>
      </div>

      <div className="mx-auto mt-20 max-w-2xl" id="faq">
        <h2 className="font-display text-2xl text-ink">Frequently asked questions</h2>
        <dl className="mt-6 divide-y divide-line">
          {faqs.map((f) => (
            <div key={f.q} className="py-4">
              <dt className="text-[15px] font-medium text-ink">{f.q}</dt>
              <dd className="mt-1.5 text-[14px] text-ink-soft">{f.a}</dd>
            </div>
          ))}
        </dl>
      </div>

      {related.length > 0 && (
        <div className="mx-auto mt-20 max-w-3xl">
          <h2 className="font-display text-2xl text-ink">Related tools</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {related.map((r) => (
              <Link
                key={r.slug}
                href={`/tools/${r.slug}`}
                className="rounded-lg border border-line bg-paper-raised px-4 py-3 text-[14px] font-medium text-ink transition hover:border-stamp"
              >
                {r.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
