"use client";

import { useRef, useState } from "react";
import { UploadCloud, FileText, Loader2, Download } from "lucide-react";
import { ApiError, downloadBlob, postForFile } from "@/lib/api";

interface QuickAction {
  label: string;
  endpoint: string;
  fieldName: string;
  extraFields?: Record<string, string>;
  resultFilename: string;
}

function actionsFor(file: File): QuickAction[] {
  const name = file.name.toLowerCase();
  if (name.endsWith(".pdf")) {
    return [
      { label: "Compress", endpoint: "/api/pdf/compress", fieldName: "file", extraFields: { level: "medium" }, resultFilename: "compressed.pdf" },
      { label: "Convert to Word", endpoint: "/api/pdf/to-word", fieldName: "file", resultFilename: "converted.docx" },
      { label: "Convert to JPG", endpoint: "/api/pdf/to-jpg", fieldName: "file", extraFields: { quality: "medium" }, resultFilename: "pages.zip" },
    ];
  }
  if (name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".png") || name.endsWith(".webp")) {
    return [{ label: "Convert to PDF", endpoint: "/api/pdf/from-images", fieldName: "files", extraFields: { page_size: "A4", orientation: "portrait" }, resultFilename: "converted.pdf" }];
  }
  if (name.endsWith(".docx") || name.endsWith(".doc")) {
    return [{ label: "Convert to PDF", endpoint: "/api/word/to-pdf", fieldName: "file", resultFilename: "converted.pdf" }];
  }
  return [];
}

export function HeroDropzone() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<{ blob: Blob; filename: string } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function pick(list: FileList | null) {
    if (!list || !list[0]) return;
    setFile(list[0]);
    setError(null);
    setDone(null);
  }

  async function run(action: QuickAction) {
    if (!file) return;
    setBusy(action.label);
    setError(null);
    try {
      const form = new FormData();
      form.append(action.fieldName, file);
      for (const [k, v] of Object.entries(action.extraFields || {})) form.append(k, v);
      const { blob, filename } = await postForFile(action.endpoint, form);
      setDone({ blob, filename: filename || action.resultFilename });
    } catch (e) {
      setError((e as ApiError).message || "Something went wrong. Please try another file.");
    } finally {
      setBusy(null);
    }
  }

  const actions = file ? actionsFor(file) : [];

  return (
    <div className="mx-auto w-full max-w-xl">
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          pick(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-line-strong bg-paper-raised px-6 py-10 text-center transition hover:border-stamp"
      >
        <UploadCloud size={30} className="mb-3 text-ink-faint" />
        <p className="text-[15px] font-medium text-ink">Drop a PDF, Word doc, or image here</p>
        <p className="mt-1 text-[13px] text-ink-faint">or click to browse — nothing uploads until you pick an action</p>
        <input ref={inputRef} type="file" className="hidden" onChange={(e) => pick(e.target.files)} />
      </div>

      {file && !done && (
        <div className="mt-4 rounded-lg border border-line bg-paper-raised p-4">
          <p className="flex items-center gap-2 text-[14px] text-ink">
            <FileText size={16} className="text-ink-faint" /> {file.name}
          </p>
          {actions.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {actions.map((a) => (
                <button
                  key={a.label}
                  onClick={() => run(a)}
                  disabled={busy !== null}
                  className="flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-[13px] font-medium text-paper transition hover:bg-stamp disabled:opacity-50"
                >
                  {busy === a.label && <Loader2 size={14} className="animate-spin" />}
                  {a.label}
                </button>
              ))}
            </div>
          ) : (
            <p className="mt-2 text-[13px] text-ink-faint">
              We don&apos;t recognize this file type yet — try browsing{" "}
              <a href="/tools" className="text-stamp underline">
                all tools
              </a>
              .
            </p>
          )}
          {error && <p className="mt-2 text-[13px] text-stamp-dark">{error}</p>}
        </div>
      )}

      {done && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-teal/30 bg-teal/5 p-4">
          <span className="text-[14px] text-ink">Your file is ready.</span>
          <button
            onClick={() => downloadBlob(done.blob, done.filename)}
            className="flex items-center gap-1.5 rounded-md bg-teal px-4 py-2 text-[13px] font-medium text-white"
          >
            <Download size={14} /> Download
          </button>
        </div>
      )}
    </div>
  );
}
