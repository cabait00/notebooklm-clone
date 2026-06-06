import type { Source } from "../types";

interface Props {
  sources: Source[];
}

export function SourceList({ sources }: Props) {
  if (sources.length === 0) return null;

  return (
    <div className="source-list">
      <div className="source-list-title">Sources</div>
      {sources.map((src, i) => (
        <div key={i} className="source-card">
          <div className="source-card-header">
            <span className="source-filename">{src.filename}</span>
            <div className="source-meta">
              <span>chunk #{src.chunk_index}</span>
              <span className="source-badge">
                {(src.similarity * 100).toFixed(0)}% match
              </span>
            </div>
          </div>
          <div className="source-snippet">{src.snippet}</div>
        </div>
      ))}
    </div>
  );
}
