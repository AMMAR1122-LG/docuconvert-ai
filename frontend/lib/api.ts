export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

/**
 * Posts a FormData payload to a backend tool endpoint and returns the
 * resulting file as a Blob, plus its suggested filename and any
 * X-* metadata headers (used by e.g. Compress to show size savings).
 */
export async function postForFile(
  path: string,
  form: FormData
): Promise<{ blob: Blob; filename: string; headers: Headers }> {
  const res = await fetch(`${API_BASE}${path}`, { method: "POST", body: form });

  if (!res.ok) {
    let message = "Something went wrong while processing your file.";
    let code = "unknown_error";
    try {
      const data = await res.json();
      message = data.error || message;
      code = data.code || code;
    } catch {
      /* response wasn't JSON (e.g. network-level failure) */
    }
    throw new ApiError(message, code, res.status);
  }

  const disposition = res.headers.get("content-disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : "result";
  const blob = await res.blob();
  return { blob, filename, headers: res.headers };
}

export async function postForJson<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) {
    throw new ApiError(data.error || "Something went wrong.", data.code || "unknown_error", res.status);
  }
  return data as T;
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
