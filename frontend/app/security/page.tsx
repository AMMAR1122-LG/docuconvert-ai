import type { Metadata } from "next";
import { ShieldCheck, Clock, Trash2, Lock } from "lucide-react";

export const metadata: Metadata = { title: "Security" };

const items = [
  { icon: ShieldCheck, t: "Secure transfer", d: "Files are sent to our servers over encrypted HTTPS connections." },
  { icon: Clock, t: "Temporary processing", d: "Documents exist only long enough to complete your request." },
  { icon: Trash2, t: "Automatic deletion", d: "Uploaded and result files are deleted automatically after a short retention window, configurable per deployment." },
  { icon: Lock, t: "Randomized storage", d: "Files are stored under randomized names, never the original filename, and never trusted by extension alone." },
];

export default function SecurityPage() {
  return (
    <div className="mx-auto max-w-2xl px-5 py-20">
      <h1 className="font-display text-3xl text-ink">Security</h1>
      <p className="mt-4 text-[15px] text-ink-soft">
        We only make claims here about protections that are actually implemented in this build.
      </p>
      <div className="mt-10 space-y-6">
        {items.map((item) => (
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
  );
}
