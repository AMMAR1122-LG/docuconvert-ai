import type { Metadata } from "next";
import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

export const metadata: Metadata = { title: "Sign up" };

export default function SignupPage() {
  return (
    <div className="mx-auto max-w-5xl px-5 py-20">
      <h1 className="mb-8 text-center font-display text-3xl text-ink">Create your free account</h1>
      <AuthForm mode="signup" />
      <p className="mt-6 text-center text-[14px] text-ink-soft">
        Already have an account? <Link href="/login" className="text-stamp">Log in</Link>
      </p>
    </div>
  );
}
