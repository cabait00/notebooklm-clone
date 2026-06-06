import type { DocumentResponse, Source } from "../types";

const BASE = "http://localhost:8000";

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/documents`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(body.detail ?? `Upload failed (${res.status})`);
  }
  return res.json() as Promise<DocumentResponse>;
}

export async function listDocuments(): Promise<DocumentResponse[]> {
  const res = await fetch(`${BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to load documents (${res.status})`);
  return res.json() as Promise<DocumentResponse[]>;
}

export async function deleteDocument(document_id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${document_id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(body.detail ?? `Delete failed (${res.status})`);
  }
}

export async function askQuestion(
  question: string,
): Promise<{ answer: string; sources: Source[]; refused: boolean }> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(body.detail ?? `Chat request failed (${res.status})`);
  }
  return res.json() as Promise<{ answer: string; sources: Source[]; refused: boolean }>;
}
