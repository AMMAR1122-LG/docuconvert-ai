import type { Metadata } from "next";
import Link from "next/link";
import { Check } from "lucide-react";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Simple, transparent pricing for DocuConvert AI — free to start, Pro for unlimited use.",
};

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: ["5 conversions per day", "10MB maximum file size", "3 AI documents per day", "Basic tools", "Ads supported"],
    cta: "Start Free",
    href: "/signup",
    highlight: false,
  },
  {
    name: "Pro",
    price: "$5",
    period: "/month",
    features: [
      "Unlimited basic conversions",
      "100MB file size",
      "OCR PDF",
      "AI PDF Assistant",
      "AI summaries & study tools",
      "Batch processing",
      "No ads",
      "Priority processing",
    ],
    cta: "Upgrade to Pro",
    href: "/signup?plan=pro",
    highlight: true,
  },
  {
    name: "Pro Annual",
    price: "$39",
    period: "/year",
    features: ["Everything in Pro", "35% cheaper than monthly", "Priority support"],
    cta: "Upgrade to Annual",
    href: "/signup?plan=pro_annual",
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-5xl px-5 py-16">
      <div className="mx-auto max-w-lg text-center">
        <h1 className="font-display text-4xl font-medium tracking-tight text-ink">Simple, transparent pricing</h1>
        <p className="mt-3 text-[16px] text-ink-soft">Start free. Upgrade when the daily limits get in your way.</p>
      </div>

      <div className="mt-14 grid gap-6 sm:grid-cols-3">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`rounded-xl border p-6 ${plan.highlight ? "border-stamp bg-paper-raised shadow-sm" : "border-line bg-paper-raised"}`}
          >
            {plan.highlight && (
              <p className="mb-3 inline-block rounded-full bg-stamp px-3 py-1 text-[12px] font-medium text-white">Most popular</p>
            )}
            <h2 className="font-display text-xl text-ink">{plan.name}</h2>
            <p className="mt-2">
              <span className="font-display text-3xl text-ink">{plan.price}</span>
              <span className="text-[14px] text-ink-faint"> {plan.period}</span>
            </p>
            <ul className="mt-6 space-y-2.5">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-[14px] text-ink-soft">
                  <Check size={16} className="mt-0.5 shrink-0 text-teal" /> {f}
                </li>
              ))}
            </ul>
            <Link
              href={plan.href}
              className={`mt-8 block rounded-md px-4 py-2.5 text-center text-[14px] font-medium transition ${
                plan.highlight ? "bg-stamp text-white hover:bg-stamp-dark" : "border border-line text-ink hover:border-stamp"
              }`}
            >
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>

      <p className="mt-10 text-center text-[13px] text-ink-faint">
        Prices shown are illustrative and configurable from the admin panel — not hardcoded in the app.
      </p>
    </div>
  );
}
