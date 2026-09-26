import type { Metadata } from "next";
export const metadata: Metadata = { title: "Contact" };

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">Contact</h1>
      <p className="mt-4 text-[15px] text-ink-soft">
        For support, billing, or partnership questions, reach us at{" "}
        <a href="mailto:support@docuconvert.ai" className="text-stamp">support@docuconvert.ai</a>.
      </p>
    </div>
  );
}
