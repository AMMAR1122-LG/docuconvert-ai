import Link from "next/link";
import { ArrowRight, ShieldCheck, Clock, Trash2, Lock, Sparkles } from "lucide-react";
import { HeroDropzone } from "@/components/HeroDropzone";
import { TOOLS } from "@/lib/tools";

const POPULAR = [
  "pdf-to-word",
  "word-to-pdf",
  "compress-pdf",
  "merge-pdf",
  "jpg-to-pdf",
  "pdf-to-jpg",
  "ocr-pdf",
];

const FAQS = [
  { q: "Is PDF to Word free?", a: "Yes — the free plan covers everyday file sizes and daily volume, with no account required to try it." },
  { q: "Are my documents secure?", a: "Files travel over HTTPS, get randomized filenames in storage, and are automatically deleted after a short retention window." },
  { q: "How large can my PDF be?", a: "10MB on the free plan, 100MB on Pro." },
  { q: "Can I convert scanned PDFs?", a: "Yes — run OCR PDF first to make a scan searchable, then use any other tool on the result." },
  { q: "Does the AI store my documents?", a: "Documents used for AI features are processed to answer your questions and are not used to train models unless you explicitly opt in." },
  { q: "Can I cancel my subscription?", a: "Yes, any time, from your billing settings — your plan stays active until the end of the paid period." },
];

export default function Home() {
  return (
    <>
      <section className="border-b border-line bg-paper">
        <div className="mx-auto max-w-6xl px-5 pb-20 pt-16 text-center sm:pt-24">
          <h1 className="mx-auto max-w-3xl font-display text-4xl font-medium leading-[1.1] tracking-tight text-ink sm:text-6xl">
            All Your Documents.
            <br />
            One Powerful Toolkit.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-[17px] text-ink-soft">
            Convert, compress, edit, OCR and chat with your documents — all in one secure platform.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link
              href="/tools"
              className="rounded-md bg-stamp px-6 py-3 text-[15px] font-medium text-white transition hover:bg-stamp-dark"
            >
              Explore All Tools
            </Link>
            <Link
              href="/ai"
              className="rounded-md border border-line px-6 py-3 text-[15px] font-medium text-ink transition hover:border-stamp"
            >
              Try AI Tools
            </Link>
          </div>

          <div className="mt-12">
            <HeroDropzone />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20">
        <div className="mb-8 flex items-end justify-between">
          <h2 className="font-display text-2xl text-ink sm:text-3xl">Popular Tools</h2>
          <Link href="/tools" className="flex items-center gap-1 text-[14px] font-medium text-stamp">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {POPULAR.map((slug) => {
            const tool = TOOLS.find((t) => t.slug === slug)!;
            return (
              <Link
                key={slug}
                href={`/tools/${slug}`}
                className="group rounded-lg border border-line bg-paper-raised p-5 transition hover:border-stamp"
              >
                <p className="font-display text-lg text-ink">{tool.name}</p>
                <p className="mt-1 text-[13px] text-ink-faint">{tool.short}</p>
                <ArrowRight
                  size={15}
                  className="mt-4 text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-stamp"
                />
              </Link>
            );
          })}
        </div>
      </section>

      <section className="border-y border-line bg-ink">
        <div className="mx-auto grid max-w-6xl gap-10 px-5 py-20 sm:grid-cols-2 sm:items-center">
          <div>
            <p className="mb-3 flex items-center gap-1.5 text-[13px] font-medium uppercase tracking-wide text-stamp">
              <Sparkles size={14} /> AI Document Assistant
            </p>
            <h2 className="font-display text-3xl font-medium leading-tight text-paper sm:text-4xl">
              Your Documents, Now Intelligent.
            </h2>
            <p className="mt-4 text-[16px] text-paper/70">
              Upload a document and let AI summarize, explain, analyze and answer questions about it — grounded in
              the actual pages, with citations, never confident fabrication.
            </p>
            <Link
              href="/ai"
              className="mt-6 inline-flex items-center gap-1.5 rounded-md bg-paper px-5 py-2.5 text-[14px] font-medium text-ink transition hover:bg-stamp hover:text-white"
            >
              Explore AI Tools <ArrowRight size={14} />
            </Link>
          </div>
          <div className="rounded-xl border border-paper/10 bg-paper/5 p-6">
            <p className="text-[13px] text-paper/50">You asked</p>
            <p className="mt-1 text-[14px] text-paper">What are the main concepts in Chapter 4?</p>
            <div className="mt-4 border-t border-paper/10 pt-4">
              <p className="text-[13px] text-paper/50">AI Assistant</p>
              <p className="mt-1 text-[14px] leading-relaxed text-paper/90">
                Chapter 4 covers three core ideas: supply and demand equilibrium, price elasticity, and market
                failure. It builds directly on the framework introduced in Chapter 2.
                <br />
                <span className="text-paper/50">Source: Page 61–68</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20">
        <h2 className="mb-10 text-center font-display text-2xl text-ink sm:text-3xl">How It Works</h2>
        <div className="grid gap-10 sm:grid-cols-3">
          {[
            { n: "1", t: "Upload", d: "Select your document." },
            { n: "2", t: "Process", d: "Our system processes your file." },
            { n: "3", t: "Download", d: "Download your result." },
          ].map((s) => (
            <div key={s.n} className="text-center">
              <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-full border border-line font-display text-ink">
                {s.n}
              </div>
              <p className="font-display text-lg text-ink">{s.t}</p>
              <p className="mt-1.5 text-[14px] text-ink-soft">{s.d}</p>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-[14px] text-ink-faint">
          For AI tools: <span className="text-ink">Upload → Ask → Get Answers</span>
        </p>
      </section>

      <section className="border-t border-line bg-paper-raised">
        <div className="mx-auto max-w-6xl px-5 py-20">
          <div className="mx-auto max-w-xl text-center">
            <h2 className="font-display text-2xl text-ink sm:text-3xl">Your documents are private.</h2>
          </div>
          <div className="mx-auto mt-10 grid max-w-3xl gap-8 sm:grid-cols-2">
            {[
              { icon: ShieldCheck, t: "Secure transfer", d: "Files are sent over encrypted HTTPS connections." },
              { icon: Clock, t: "Temporary processing", d: "Documents exist only long enough to process your request." },
              { icon: Trash2, t: "Automatic deletion", d: "Files are deleted automatically after a short retention window." },
              { icon: Lock, t: "No selling documents", d: "We never sell your documents, and AI doesn't train on them unless you opt in." },
            ].map((item) => (
              <div key={item.t} className="flex gap-3">
                <item.icon size={20} className="mt-0.5 shrink-0 text-stamp" />
                <div>
                  <p className="text-[15px] font-medium text-ink">{item.t}</p>
                  <p className="mt-0.5 text-[14px] text-ink-soft">{item.d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-5 py-20" id="faq">
        <h2 className="mb-8 text-center font-display text-2xl text-ink sm:text-3xl">Frequently Asked Questions</h2>
        <dl className="divide-y divide-line">
          {FAQS.map((f) => (
            <div key={f.q} className="py-5">
              <dt className="text-[15px] font-medium text-ink">{f.q}</dt>
              <dd className="mt-1.5 text-[14px] text-ink-soft">{f.a}</dd>
            </div>
          ))}
        </dl>
      </section>
    </>
  );
}
