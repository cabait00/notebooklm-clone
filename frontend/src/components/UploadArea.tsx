import { useRef, useState } from "react";

interface Props {
  onUpload: (file: File) => void;
  uploading: boolean;
  error: string | null;
}

export function UploadArea({ onUpload, uploading, error }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    onUpload(files[0]);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div
      className={`upload-area${dragging ? " dragging" : ""}${uploading ? " uploading" : ""}`}
      onClick={() => !uploading && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (!uploading) handleFiles(e.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md,.markdown"
        onChange={(e) => handleFiles(e.target.files)}
        disabled={uploading}
      />
      <span className="upload-icon">
        {uploading ? <span className="spinner" /> : "📄"}
      </span>
      <span className="upload-label">
        {uploading ? "Uploading…" : "Upload document"}
      </span>
      <span className="upload-hint">PDF, TXT, or Markdown · click or drag & drop</span>
      {error && <div className="upload-error">{error}</div>}
    </div>
  );
}
