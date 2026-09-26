"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE } from "@/lib/api";

interface Usage {
  plan: string;
  conversions_last_30d: number;
  ai_requests_last_30d: number;
  storage_used_bytes: number;
}

export default function DashboardPage() {
  const [usage, setUsage] = useState<Usage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("Log in to see your dashboard.");
      return;
    }
    fetch(`${API_BASE}/api/user/usage`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (res) => {
        if (!res.ok) throw new Error((await res.json()).error);
        return res.json();
      })
      .then(setUsage)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="mx-auto max-w-lg px-5 py-24 text-center">
        <p className="text-[15px] text-ink-soft">{error}</p>
        <Link href="/login" className="mt-4 inline-block rounded-md bg-ink px-5 py-2.5 text-[14px] text-paper">
          Log in
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-16">
      <h1 className="font-display text-3xl text-ink">Dashboard</h1>

      {usage ? (
        <div className="mt-10 grid gap-4 sm:grid-cols-4">
          {[
            { label: "Plan", value: usage.plan },
            { label: "Conversions (30d)", value: usage.conversions_last_30d },
            { label: "AI requests (30d)", value: usage.ai_requests_last_30d },
            { label: "Storage used", value: `${(usage.storage_used_bytes / 1024 / 1024).toFixed(1)} MB` },
          ].map((s) => (
            <div key={s.label} className="rounded-lg border border-line bg-paper-raised p-5">
              <p className="text-[13px] text-ink-faint">{s.label}</p>
              <p className="mt-1 font-display text-2xl capitalize text-ink">{s.value}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-8 text-[14px] text-ink-faint">Loading…</p>
      )}

      <div className="mt-12">
        <h2 className="font-display text-xl text-ink">Recent files</h2>
        <p className="mt-2 text-[14px] text-ink-faint">
          Files you process while logged in will appear here, with download, delete, and reprocess actions.
        </p>
      </div>
    </div>
  );
}
