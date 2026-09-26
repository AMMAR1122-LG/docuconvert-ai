import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Blog",
  description: "Guides on PDFs, productivity, and document management.",
};

const POSTS = [
  { title: "How to Convert PDF to Word Without Losing Formatting", category: "PDF Guides" },
  { title: "How to Compress a PDF Without Losing Quality", category: "PDF Guides" },
  { title: "How to Extract Text from a Scanned PDF", category: "Document Management" },
  { title: "How to Convert JPG Images to PDF", category: "PDF Guides" },
  { title: "How to Make a PDF Searchable with OCR", category: "Document Management" },
  { title: "How to Summarize a Long PDF Using AI", category: "AI" },
];

export default function BlogPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-20">
      <h1 className="font-display text-4xl font-medium tracking-tight text-ink">Blog</h1>
      <p className="mt-3 text-[16px] text-ink-soft">Guides on PDFs, productivity, and document management.</p>

      <div className="mt-12 divide-y divide-line">
        {POSTS.map((post) => (
          <Link key={post.title} href="#" className="group block py-5">
            <p className="text-[13px] font-medium uppercase tracking-wide text-stamp">{post.category}</p>
            <p className="mt-1 text-[17px] font-medium text-ink group-hover:text-stamp">{post.title}</p>
          </Link>
        ))}
      </div>
      <p className="mt-10 text-[13px] text-ink-faint">
        Article content is managed from the admin panel (BlogPost model) — these are placeholder entries.
      </p>
    </div>
  );
}
