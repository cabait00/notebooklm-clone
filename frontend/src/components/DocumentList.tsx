import type { DocumentResponse } from "../types";

interface Props {
  documents: DocumentResponse[];
  onDelete: (document_id: string) => void;
  deletingId: string | null;
}

const FILE_ICONS: Record<string, string> = {
  pdf: "📕",
  txt: "📄",
  md: "📝",
};

export function DocumentList({ documents, onDelete, deletingId }: Props) {
  if (documents.length === 0) {
    return (
      <div className="document-list">
        <p className="document-list-empty">
          No documents yet.<br />Upload one to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="document-list">
      {documents.map((doc) => {
        const isDeleting = deletingId === doc.document_id;
        return (
          <div key={doc.document_id} className="document-item">
            <span className="doc-icon">{FILE_ICONS[doc.file_type] ?? "📄"}</span>
            <div className="doc-info">
              <div className="doc-name" title={doc.filename}>
                {doc.filename}
              </div>
              <div className="doc-meta">
                {doc.chunk_count} chunks · {(doc.character_count / 1000).toFixed(1)}k chars
              </div>
            </div>
            <button
              className="delete-btn"
              title="Delete document"
              disabled={isDeleting || deletingId !== null}
              onClick={() => onDelete(doc.document_id)}
              aria-label={`Delete ${doc.filename}`}
            >
              {isDeleting ? <span className="spinner spinner-sm" /> : "×"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
