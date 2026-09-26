export type FieldType = "select" | "text" | "number" | "range";

export interface ToolField {
  name: string;
  label: string;
  type: FieldType;
  options?: { value: string; label: string }[];
  default?: string | number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  helpText?: string;
}

export type ResultKind = "file" | "zip" | "text";

export interface ToolConfig {
  endpoint: string; // path on the API, e.g. /api/pdf/merge
  accept: string; // input[accept] value
  multiple: boolean;
  minFiles?: number;
  fileFieldName: string; // "file" or "files"
  fields?: ToolField[];
  resultKind: ResultKind;
  resultFilenameFallback: string;
  actionLabel: string;
  showCompressionStats?: boolean;
}

export const TOOL_CONFIGS: Record<string, ToolConfig> = {
  "merge-pdf": {
    endpoint: "/api/pdf/merge",
    accept: "application/pdf",
    multiple: true,
    minFiles: 2,
    fileFieldName: "files",
    resultKind: "file",
    resultFilenameFallback: "merged.pdf",
    actionLabel: "Merge PDFs",
  },
  "split-pdf": {
    endpoint: "/api/pdf/split",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      {
        name: "mode",
        label: "Split mode",
        type: "select",
        options: [
          { value: "all", label: "Every page as its own PDF" },
          { value: "ranges", label: "Custom page ranges" },
        ],
        default: "all",
      },
      {
        name: "ranges",
        label: "Page ranges",
        type: "text",
        placeholder: "e.g. 1-5,6-10,11-20",
        helpText: "Only used with Custom page ranges.",
      },
    ],
    resultKind: "zip",
    resultFilenameFallback: "split.zip",
    actionLabel: "Split PDF",
  },
  "compress-pdf": {
    endpoint: "/api/pdf/compress",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      {
        name: "level",
        label: "Compression level",
        type: "select",
        options: [
          { value: "low", label: "Low — best quality" },
          { value: "medium", label: "Medium — balanced" },
          { value: "high", label: "High — smallest file" },
        ],
        default: "medium",
      },
    ],
    resultKind: "file",
    resultFilenameFallback: "compressed.pdf",
    actionLabel: "Compress PDF",
    showCompressionStats: true,
  },
  "pdf-to-word": {
    endpoint: "/api/pdf/to-word",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    resultKind: "file",
    resultFilenameFallback: "converted.docx",
    actionLabel: "Convert to Word",
  },
  "word-to-pdf": {
    endpoint: "/api/word/to-pdf",
    accept: ".doc,.docx",
    multiple: false,
    fileFieldName: "file",
    resultKind: "file",
    resultFilenameFallback: "converted.pdf",
    actionLabel: "Convert to PDF",
  },
  "pdf-to-jpg": {
    endpoint: "/api/pdf/to-jpg",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      {
        name: "quality",
        label: "Image quality",
        type: "select",
        options: [
          { value: "low", label: "Low" },
          { value: "medium", label: "Medium" },
          { value: "high", label: "High" },
        ],
        default: "medium",
      },
    ],
    resultKind: "zip",
    resultFilenameFallback: "pages.zip",
    actionLabel: "Convert to JPG",
  },
  "jpg-to-pdf": {
    endpoint: "/api/pdf/from-images",
    accept: "image/jpeg,image/png,image/webp",
    multiple: true,
    minFiles: 1,
    fileFieldName: "files",
    fields: [
      {
        name: "page_size",
        label: "Page size",
        type: "select",
        options: [
          { value: "A4", label: "A4" },
          { value: "Letter", label: "Letter" },
        ],
        default: "A4",
      },
      {
        name: "orientation",
        label: "Orientation",
        type: "select",
        options: [
          { value: "portrait", label: "Portrait" },
          { value: "landscape", label: "Landscape" },
        ],
        default: "portrait",
      },
    ],
    resultKind: "file",
    resultFilenameFallback: "converted.pdf",
    actionLabel: "Convert to PDF",
  },
  "pdf-to-excel": {
    endpoint: "/api/pdf/to-excel",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    resultKind: "file",
    resultFilenameFallback: "converted.xlsx",
    actionLabel: "Convert to Excel",
  },
  "pdf-to-ppt": {
    endpoint: "/api/pdf/to-ppt",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    resultKind: "file",
    resultFilenameFallback: "converted.pptx",
    actionLabel: "Convert to PowerPoint",
  },
  "rotate-pdf": {
    endpoint: "/api/pdf/rotate",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      {
        name: "degrees",
        label: "Rotate by",
        type: "select",
        options: [
          { value: "90", label: "90°" },
          { value: "180", label: "180°" },
          { value: "270", label: "270°" },
        ],
        default: "90",
      },
      {
        name: "pages",
        label: "Pages (optional)",
        type: "text",
        placeholder: "e.g. 1,3,5 — leave blank for all pages",
      },
    ],
    resultKind: "file",
    resultFilenameFallback: "rotated.pdf",
    actionLabel: "Rotate PDF",
  },
  "pdf-to-text": {
    endpoint: "/api/pdf/to-text",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    resultKind: "text",
    resultFilenameFallback: "extracted.txt",
    actionLabel: "Extract Text",
  },
  "ocr-pdf": {
    endpoint: "/api/pdf/ocr",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      {
        name: "languages",
        label: "Language",
        type: "select",
        options: [
          { value: "english", label: "English" },
          { value: "arabic", label: "Arabic" },
          { value: "urdu", label: "Urdu" },
        ],
        default: "english",
      },
    ],
    resultKind: "file",
    resultFilenameFallback: "searchable.pdf",
    actionLabel: "Run OCR",
  },
  "watermark-pdf": {
    endpoint: "/api/pdf/watermark",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [
      { name: "text", label: "Watermark text", type: "text", placeholder: "e.g. CONFIDENTIAL", default: "CONFIDENTIAL" },
      { name: "opacity", label: "Opacity", type: "range", min: 0.1, max: 0.8, step: 0.1, default: 0.3 },
    ],
    resultKind: "file",
    resultFilenameFallback: "watermarked.pdf",
    actionLabel: "Add Watermark",
  },
  "delete-pdf-pages": {
    endpoint: "/api/pdf/delete-pages",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [{ name: "pages", label: "Pages to delete", type: "text", placeholder: "e.g. 2,4,7" }],
    resultKind: "file",
    resultFilenameFallback: "edited.pdf",
    actionLabel: "Delete Pages",
  },
  "extract-pdf-pages": {
    endpoint: "/api/pdf/extract-pages",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [{ name: "pages", label: "Pages to keep", type: "text", placeholder: "e.g. 1,3,5-7" }],
    resultKind: "file",
    resultFilenameFallback: "extracted.pdf",
    actionLabel: "Extract Pages",
  },
  "password-protect-pdf": {
    endpoint: "/api/pdf/protect",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [{ name: "password", label: "Password", type: "text", placeholder: "Choose a password" }],
    resultKind: "file",
    resultFilenameFallback: "protected.pdf",
    actionLabel: "Protect PDF",
  },
  "unlock-pdf": {
    endpoint: "/api/pdf/unlock",
    accept: "application/pdf",
    multiple: false,
    fileFieldName: "file",
    fields: [{ name: "password", label: "Password", type: "text", placeholder: "Enter the current password" }],
    resultKind: "file",
    resultFilenameFallback: "unlocked.pdf",
    actionLabel: "Unlock PDF",
  },
};
