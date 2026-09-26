import type { Metadata } from "next";
export const metadata: Metadata = { title: "Privacy Policy" };

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">Privacy Policy</h1>
      <p className="mt-2 text-[13px] text-ink-faint">
        Placeholder structure — review with a lawyer before publishing. Not copied from another company.
      </p>
      <div className="mt-8 space-y-6 text-[14px] leading-relaxed text-ink-soft">
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">1. What we collect</h2>
          <p>Account details you provide (name, email), files you upload for processing, and basic usage metrics.</p>
        </section>
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">2. How files are handled</h2>
          <p>Files are processed to fulfill your request and deleted automatically after a short retention window. We do not sell documents.</p>
        </section>
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">3. AI features</h2>
          <p>Documents used with AI tools are not used to train models unless you explicitly opt in.</p>
        </section>
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">4. Your rights</h2>
          <p>You may request deletion of your account and associated data at any time.</p>
        </section>
      </div>
    </div>
  );
}
