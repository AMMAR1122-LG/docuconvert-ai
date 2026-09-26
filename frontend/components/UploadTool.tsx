"use client";

import { useRef, useState } from "react";
import { UploadCloud, FileText, X, Loader2, Download, AlertCircle } from "lucide-react";
import { ApiError, downloadBlob, postForFile, postForJson } from "@/lib/api";
import type { ToolConfig } from "@/lib/toolConfigs";

interface Props {
  config: ToolConfig;
}

type Status = "idle" | "ready" | "processing" | "done" | "error";

export function UploadTool({ config }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [values, setValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const f of config.fields || []) {
      if (f.default !== undefined) initial[f.name] = String(f.default);
    }
    return initial;
  });
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [resultText, setResultText] = useState<string | null>(null);
  const [resultBlob, setResultBlob] = useState<{ blob: Blob; filename: string } | null>(null);
  const [stats, setStats] = useState<{ original: number; compressed: number; pct: number } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const canSubmit = config.multiple ? files.length >= (config.minFiles || 1) : files.length === 1;

  function addFiles(list: FileList | null) {
    if (!list) return;
    const incoming = Array.from(list);
    setFiles(config.multiple ? [...files, ...incoming] : [incoming[0]]);
    setStatus("ready");
    setError(null);
  }

  function removeFile(idx: number) {
    const next = files.filter((_, i) => i !== idx);
    setFiles(next);
    setStatus(next.length ? "ready" : "idle");
  }

  function reset() {
    setFiles([]);
    setStatus("idle");
    setError(null);
    setResultText(null);
    setResultBlob(null);
    setStats(null);
  }

  async function handleSubmit() {
    setStatus("processing");
    setError(null);
    const form = new FormData();
    for (const f of files) form.append(config.fileFieldName, f);
    for (const [key, val] of Object.entries(values)) form.append(key, val);

    try {
      if (config.resultKind === "text") {
        const data = await postForJson<{ text: string }>(config.endpoint, form);
        setResultText(data.text);
        setStatus("done");
        return;
      }

      const { blob, filename, headers } = await postForFile(config.endpoint, form);
      setResultBlob({ blob, filename: filename || config.resultFilenameFallback });

      if (config.showCompressionStats) {
        const original = Number(headers.get("x-original-size") || 0);
        const compressed = Number(headers.get("x-compressed-size") || 0);
        const pct = Number(headers.get("x-percent-saved") || 0);
        if (original) setStats({ original, compressed, pct });
      }
      setStatus("done");
    } catch (e) {
      const err = e as ApiError;
      setError(err.message || "We couldn't process this document. Please try another file.");
      setStatus("error");
    }
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      {status !== "done" && (
        <>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              addFiles(e.dataTransfer.files);
            }}
            onClick={() => inputRef.current?.click()}
            className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-line-strong bg-paper-raised px-6 py-12 text-center transition hover:border-stamp"
          >
            <UploadCloud size={32} className="mb-3 text-ink-faint" />
            <p className="text-[15px] font-medium text-ink">
              Drop your file{config.multiple ? "s" : ""} here, or click to browse
            </p>
            <p className="mt-1 text-[13px] text-ink-faint">Maximum 10MB on the free plan</p>
            <input
              ref={inputRef}
              type="file"
              accept={config.accept}
              multiple={config.multiple}
              className="hidden"
              onChange={(e) => addFiles(e.target.files)}
            />
          </div>

          {files.length > 0 && (
            <ul className="mt-4 space-y-2">
              {files.map((f, i) => (
                <li
                  key={`${f.name}-${i}`}
                  className="flex items-center justify-between rounded-lg border border-line bg-paper-raised px-4 py-2.5"
                >
                  <span className="flex items-center gap-2 truncate text-[14px] text-ink">
                    <FileText size={16} className="shrink-0 text-ink-faint" />
                    <span className="truncate">{f.name}</span>
                    <span className="shrink-0 text-ink-faint">({(f.size / 1024).toFixed(0)} KB)</span>
                  </span>
                  <button onClick={() => removeFile(i)} aria-label={`Remove ${f.name}`}>
                    <X size={16} className="text-ink-faint hover:text-stamp" />
                  </button>
                </li>
              ))}
            </ul>
          )}

          {config.fields && config.fields.length > 0 && (
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {config.fields.map((field) => (
                <div key={field.name} className={field.type === "range" ? "sm:col-span-2" : ""}>
                  <label className="mb-1.5 block text-[13px] font-medium text-ink-soft">{field.label}</label>
                  {field.type === "select" && (
                    <select
                      value={values[field.name] ?? ""}
                      onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                      className="w-full rounded-md border border-line bg-paper-raised px-3 py-2 text-[14px] text-ink"
                    >
                      {field.options?.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  )}
                  {field.type === "text" && (
                    <input
                      type="text"
                      placeholder={field.placeholder}
                      value={values[field.name] ?? ""}
                      onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                      className="w-full rounded-md border border-line bg-paper-raised px-3 py-2 text-[14px] text-ink placeholder:text-ink-faint"
                    />
                  )}
                  {field.type === "range" && (
                    <input
                      type="range"
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      value={values[field.name] ?? field.default}
                      onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                      className="w-full accent-stamp"
                    />
                  )}
                  {field.helpText && <p className="mt-1 text-[12px] text-ink-faint">{field.helpText}</p>}
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-md border border-stamp/30 bg-stamp/5 px-3 py-2.5 text-[14px] text-stamp-dark">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!canSubmit || status === "processing"}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-md bg-ink px-5 py-3 text-[15px] font-medium text-paper transition hover:bg-stamp disabled:cursor-not-allowed disabled:opacity-40"
          >
            {status === "processing" ? (
              <>
                <Loader2 size={17} className="animate-spin" /> Processing your document…
              </>
            ) : (
              config.actionLabel
            )}
          </button>
        </>
      )}

      {status === "done" && (
        <div className="rounded-xl border border-line bg-paper-raised p-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-teal/10">
            <Download size={22} className="text-teal" />
          </div>
          <h3 className="font-display text-xl text-ink">Your document is ready</h3>

          {stats && (
            <p className="mt-2 text-[14px] text-ink-soft">
              {(stats.original / 1024 / 1024).toFixed(1)} MB → {(stats.compressed / 1024 / 1024).toFixed(1)} MB —{" "}
              <span className="font-medium text-teal">{stats.pct}% smaller</span>
            </p>
          )}

          {resultText !== null && (
            <textarea
              readOnly
              value={resultText}
              className="mt-4 h-56 w-full rounded-md border border-line bg-paper p-3 text-left text-[13px] text-ink-soft"
            />
          )}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
            {resultBlob && (
              <button
                onClick={() => downloadBlob(resultBlob.blob, resultBlob.filename)}
                className="rounded-md bg-ink px-5 py-2.5 text-[14px] font-medium text-paper hover:bg-stamp"
              >
                Download {resultBlob.filename}
              </button>
            )}
            {resultText !== null && (
              <>
                <button
                  onClick={() => navigator.clipboard.writeText(resultText)}
                  className="rounded-md border border-line px-5 py-2.5 text-[14px] font-medium text-ink hover:border-stamp"
                >
                  Copy text
                </button>
                <button
                  onClick={() =>
                    downloadBlob(new Blob([resultText], { type: "text/plain" }), config.resultFilenameFallback)
                  }
                  className="rounded-md border border-line px-5 py-2.5 text-[14px] font-medium text-ink hover:border-stamp"
                >
                  Download .txt
                </button>
              </>
            )}
            <button
              onClick={reset}
              className="rounded-md border border-line px-5 py-2.5 text-[14px] font-medium text-ink-soft hover:border-stamp"
            >
              Process another file
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
