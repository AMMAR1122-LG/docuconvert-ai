export type ToolCategory = "Convert" | "Organize" | "Edit" | "Security" | "AI";

export interface ToolDef {
  slug: string;
  name: string;
  short: string;
  description: string;
  category: ToolCategory;
  /** Implemented against the live backend in this build. */
  live: boolean;
}

export const TOOLS: ToolDef[] = [
  { slug: "merge-pdf", name: "Merge PDF", short: "Combine PDFs in order", description: "Combine multiple PDF files into a single document, in the order you choose.", category: "Organize", live: true },
  { slug: "split-pdf", name: "Split PDF", short: "Pull pages apart", description: "Split a PDF into individual pages or custom page ranges.", category: "Organize", live: true },
  { slug: "compress-pdf", name: "Compress PDF", short: "Shrink file size", description: "Reduce PDF file size while keeping it readable, with a choice of compression levels.", category: "Organize", live: true },
  { slug: "pdf-to-word", name: "PDF to Word", short: "PDF → editable .docx", description: "Convert a PDF into an editable Word document.", category: "Convert", live: true },
  { slug: "word-to-pdf", name: "Word to PDF", short: ".docx → PDF", description: "Convert a Word document into a PDF, preserving layout.", category: "Convert", live: true },
  { slug: "pdf-to-jpg", name: "PDF to JPG", short: "Pages → images", description: "Turn each page of a PDF into a JPG image.", category: "Convert", live: true },
  { slug: "jpg-to-pdf", name: "JPG to PDF", short: "Images → PDF", description: "Combine JPG, PNG or WebP images into one PDF.", category: "Convert", live: true },
  { slug: "pdf-to-excel", name: "PDF to Excel", short: "Extract tables", description: "Extract tables from a PDF into an editable spreadsheet.", category: "Convert", live: true },
  { slug: "pdf-to-ppt", name: "PDF to PowerPoint", short: "Pages → slides", description: "Turn PDF pages into a PowerPoint presentation.", category: "Convert", live: true },
  { slug: "rotate-pdf", name: "Rotate PDF", short: "Fix page orientation", description: "Rotate one, several, or all pages in a PDF.", category: "Edit", live: true },
  { slug: "pdf-to-text", name: "PDF to Text", short: "Extract plain text", description: "Pull the plain text out of a PDF to copy or download.", category: "Convert", live: true },
  { slug: "ocr-pdf", name: "OCR PDF", short: "Make scans searchable", description: "Run OCR on a scanned PDF so its text becomes selectable and searchable.", category: "Edit", live: true },
  { slug: "watermark-pdf", name: "Watermark PDF", short: "Stamp every page", description: "Add a text watermark across every page of a PDF.", category: "Edit", live: true },
  { slug: "delete-pdf-pages", name: "Delete PDF Pages", short: "Remove pages", description: "Remove specific pages from a PDF.", category: "Edit", live: true },
  { slug: "extract-pdf-pages", name: "Extract PDF Pages", short: "Keep only some pages", description: "Pull out just the pages you need into a new PDF.", category: "Edit", live: true },
  { slug: "password-protect-pdf", name: "Password Protect PDF", short: "Lock with a password", description: "Add a password so only people you share it with can open the PDF.", category: "Security", live: true },
  { slug: "unlock-pdf", name: "Unlock PDF", short: "Remove a password", description: "Remove a password from a PDF you have the password for.", category: "Security", live: true },
  { slug: "sign-pdf", name: "Sign PDF", short: "Add a signature", description: "Add a signature image or text to a PDF.", category: "Edit", live: false },
];

export const AI_TOOLS = [
  { slug: "pdf-chat", name: "Chat with a PDF", description: "Ask questions about a document and get answers grounded in its actual pages, with citations." },
  { slug: "summarize-pdf", name: "Summarize a PDF", description: "Get a short, medium, or detailed summary of a long document." },
  { slug: "generate-notes", name: "Generate Study Notes", description: "Turn a textbook chapter into structured revision notes." },
  { slug: "generate-mcqs", name: "Generate MCQs", description: "Create multiple-choice questions from any document, with explanations." },
  { slug: "translate-document", name: "Translate a Document", description: "Translate selected text from an uploaded document." },
  { slug: "extract-data", name: "Extract Data", description: "Pull structured data — tables, line items, fields — out of a document." },
];

export function getTool(slug: string): ToolDef | undefined {
  return TOOLS.find((t) => t.slug === slug);
}
