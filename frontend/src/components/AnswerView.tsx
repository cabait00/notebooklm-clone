import type { Source } from "../types";
import { SourceList } from "./SourceList";

interface Props {
  answer: string;
  sources: Source[];
  refused: boolean;
}

export function AnswerView({ answer, sources, refused }: Props) {
  return (
    <div className="answer-view">
      <div className={`answer-card${refused ? " refused" : ""}`}>
        {refused && (
          <div className="answer-refused-badge">⚠ Insufficient evidence</div>
        )}
        <div className="answer-text">{answer}</div>
      </div>
      {!refused && <SourceList sources={sources} />}
    </div>
  );
}
