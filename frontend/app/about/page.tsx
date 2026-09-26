import type { Metadata } from "next";
export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">About DocuConvert AI</h1>
      <p className="mt-4 text-[15px] leading-relaxed text-ink-soft">
        DocuConvert AI is a document toolkit built to make everyday PDF and document work faster —
        converting, compressing, organizing, and understanding documents without installing desktop
        software. It&apos;s built to run at any scale, from a single user trying one tool to a business
        processing thousands of documents a day.
      </p>
    </div>
  );
}
