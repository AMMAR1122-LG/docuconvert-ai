"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { API_BASE } from "@/lib/api";

interface Props {
  mode: "login" | "signup";
}

export function AuthForm({ mode }: Props) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (mode === "signup" && password !== confirm) {
      setError("Passwords don't match.");
      return;
    }

    setLoading(true);
    try {
      const path = mode === "signup" ? "/api/auth/register" : "/api/auth/login";
      const body = mode === "signup" ? { name, email, password } : { email, password };
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Something went wrong.");
        return;
      }
      localStorage.setItem("access_token", data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Couldn't reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto w-full max-w-sm">
      {mode === "signup" && (
        <div className="mb-4">
          <label className="mb-1.5 block text-[13px] font-medium text-ink-soft">Name</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-line bg-paper-raised px-3 py-2.5 text-[14px] text-ink"
          />
        </div>
      )}
      <div className="mb-4">
        <label className="mb-1.5 block text-[13px] font-medium text-ink-soft">Email</label>
        <input
          required
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-line bg-paper-raised px-3 py-2.5 text-[14px] text-ink"
        />
      </div>
      <div className="mb-4">
        <label className="mb-1.5 block text-[13px] font-medium text-ink-soft">Password</label>
        <input
          required
          type="password"
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-line bg-paper-raised px-3 py-2.5 text-[14px] text-ink"
        />
      </div>
      {mode === "signup" && (
        <div className="mb-4">
          <label className="mb-1.5 block text-[13px] font-medium text-ink-soft">Confirm password</label>
          <input
            required
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full rounded-md border border-line bg-paper-raised px-3 py-2.5 text-[14px] text-ink"
          />
        </div>
      )}

      {error && <p className="mb-4 text-[13px] text-stamp-dark">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2.5 text-[14px] font-medium text-paper transition hover:bg-stamp disabled:opacity-50"
      >
        {loading && <Loader2 size={16} className="animate-spin" />}
        {mode === "signup" ? "Create free account" : "Log in"}
      </button>

      <button
        type="button"
        disabled
        title="Set GOOGLE_CLIENT_ID/SECRET on the backend to enable this"
        className="mt-3 w-full rounded-md border border-line px-4 py-2.5 text-[14px] font-medium text-ink-faint"
      >
        Continue with Google
      </button>
    </form>
  );
}
