import type { Metadata } from "next";
export const metadata: Metadata = { title: "Terms of Service" };

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">Terms of Service</h1>
      <p className="mt-2 text-[13px] text-ink-faint">
        Placeholder structure — review with a lawyer before publishing.
      </p>
      <div className="mt-8 space-y-6 text-[14px] leading-relaxed text-ink-soft">
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">1. Acceptable use</h2>
          <p>Don&apos;t use DocuConvert AI to process content you don&apos;t have the rights to, or to attempt to abuse or overload the service.</p>
        </section>
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">2. Plans and billing</h2>
          <p>Subscriptions renew automatically until canceled. Cancel any time from your billing settings.</p>
        </section>
        <section>
          <h2 className="mb-2 font-display text-lg text-ink">3. Service availability</h2>
          <p>We aim for high availability but don&apos;t guarantee uninterrupted service.</p>
        </section>
      </div>
    </div>
  );
}
