import type { MetadataRoute } from "next";
import { TOOLS, AI_TOOLS } from "@/lib/tools";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://docuconvert.ai";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPages = ["", "/tools", "/ai", "/pricing", "/about", "/contact", "/blog", "/security", "/privacy", "/terms"];

  return [
    ...staticPages.map((path) => ({ url: `${BASE_URL}${path}`, lastModified: new Date() })),
    ...TOOLS.map((t) => ({ url: `${BASE_URL}/tools/${t.slug}`, lastModified: new Date() })),
    ...AI_TOOLS.map((t) => ({ url: `${BASE_URL}/ai/${t.slug}`, lastModified: new Date() })),
  ];
}
