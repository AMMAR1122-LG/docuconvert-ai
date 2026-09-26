"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, FileStack } from "lucide-react";

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-paper/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-2">
          <FileStack size={22} strokeWidth={2} className="text-stamp" />
          <span className="font-display text-lg font-medium tracking-tight text-ink">
            DocuConvert <span className="text-stamp">AI</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-8 text-[15px] text-ink-soft md:flex">
          <Link href="/tools" className="hover:text-ink">All Tools</Link>
          <Link href="/ai" className="hover:text-ink">AI Tools</Link>
          <Link href="/pricing" className="hover:text-ink">Pricing</Link>
          <Link href="/blog" className="hover:text-ink">Blog</Link>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link href="/login" className="text-[15px] text-ink-soft hover:text-ink">Log in</Link>
          <Link
            href="/signup"
            className="rounded-md bg-ink px-4 py-2 text-[15px] font-medium text-paper transition hover:bg-stamp"
          >
            Sign up free
          </Link>
        </div>

        <button
          aria-label={open ? "Close menu" : "Open menu"}
          className="md:hidden"
          onClick={() => setOpen(!open)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <nav className="flex flex-col gap-1 border-t border-line bg-paper px-5 py-4 text-[15px] md:hidden">
          <Link href="/tools" className="py-2 text-ink-soft" onClick={() => setOpen(false)}>All Tools</Link>
          <Link href="/ai" className="py-2 text-ink-soft" onClick={() => setOpen(false)}>AI Tools</Link>
          <Link href="/pricing" className="py-2 text-ink-soft" onClick={() => setOpen(false)}>Pricing</Link>
          <Link href="/blog" className="py-2 text-ink-soft" onClick={() => setOpen(false)}>Blog</Link>
          <div className="mt-2 flex gap-3 border-t border-line pt-3">
            <Link href="/login" className="flex-1 rounded-md border border-line py-2 text-center">Log in</Link>
            <Link href="/signup" className="flex-1 rounded-md bg-ink py-2 text-center text-paper">Sign up</Link>
          </div>
        </nav>
      )}
    </header>
  );
}
