import type { Metadata } from "next";
import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage() {
  return (
    <div className="mx-auto max-w-5xl px-5 py-20">
      <h1 className="mb-8 text-center font-display text-3xl text-ink">Welcome back</h1>
      <AuthForm mode="login" />
      <p className="mt-6 text-center text-[14px] text-ink-soft">
        No account? <Link href="/signup" className="text-stamp">Sign up free</Link>
      </p>
    </div>
  );
}
