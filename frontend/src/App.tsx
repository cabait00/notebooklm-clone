import { useCallback, useEffect, useState } from "react";
import "./App.css";
import { askQuestion, deleteDocument, listDocuments, uploadDocument } from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentList } from "./components/DocumentList";
import { UploadArea } from "./components/UploadArea";
import type { ChatEntry, DocumentResponse } from "./types";

let nextId = 0;

export default function App() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatEntry[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch(() => {
        // backend not reachable on first load — silently ignore
      });
  }, []);

  const handleUpload = useCallback(async (file: File) => {
    setUploading(true);
    setUploadError(null);
    try {
      const doc = await uploadDocument(file);
      setDocuments((prev) => [...prev, doc]);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDelete = useCallback(async (document_id: string) => {
    setDeletingId(document_id);
    setDeleteError(null);
    try {
      await deleteDocument(document_id);
      setDocuments((prev) => prev.filter((d) => d.document_id !== document_id));
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Deletion failed");
    } finally {
      setDeletingId(null);
    }
  }, []);

  const handleAsk = useCallback(async (question: string) => {
    setAsking(true);
    try {
      const result = await askQuestion(question);
      setChatHistory((prev) => [
        ...prev,
        {
          id: String(++nextId),
          question,
          answer: result.answer,
          sources: result.sources,
          refused: result.refused,
        },
      ]);
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        {
          id: String(++nextId),
          question,
          answer: err instanceof Error ? err.message : "An unexpected error occurred.",
          sources: [],
          refused: false,
        },
      ]);
    } finally {
      setAsking(false);
    }
  }, []);

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>NotebookLM Clone</h1>
        <span className="app-subtitle">Source-grounded answers from your documents</span>
      </header>

      <div className="app-body">
        <aside className="sidebar">
          <div className="sidebar-section">
            <h2>Upload</h2>
            <UploadArea
              onUpload={handleUpload}
              uploading={uploading}
              error={uploadError}
            />
          </div>
          <div className="sidebar-section sidebar-docs">
            <h2>Documents ({documents.length})</h2>
            {deleteError && (
              <div className="sidebar-error">{deleteError}</div>
            )}
            <DocumentList
              documents={documents}
              onDelete={handleDelete}
              deletingId={deletingId}
            />
          </div>
        </aside>

        <main className="main-area">
          <ChatPanel
            entries={chatHistory}
            asking={asking}
            onAsk={handleAsk}
          />
        </main>
      </div>
    </div>
  );
}
