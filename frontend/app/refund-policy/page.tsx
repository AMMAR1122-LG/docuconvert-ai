import type { Metadata } from "next";
export const metadata: Metadata = { title: "Refund Policy" };

export default function RefundPolicyPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">Refund Policy</h1>
      <p className="mt-2 text-[13px] text-ink-faint">Placeholder structure — review with a lawyer before publishing.</p>
      <p className="mt-8 text-[14px] leading-relaxed text-ink-soft">
        Pro subscriptions can be canceled at any time and remain active until the end of the current billing
        period. Refund eligibility for annual plans is evaluated on a case-by-case basis within 14 days of purchase.
      </p>
    </div>
  );
}
