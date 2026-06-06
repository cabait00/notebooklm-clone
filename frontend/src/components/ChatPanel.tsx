import { useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import type { ChatEntry } from "../types";
import { AnswerView } from "./AnswerView";

interface Props {
  entries: ChatEntry[];
  asking: boolean;
  onAsk: (question: string) => void;
}

export function ChatPanel({ entries, asking, onAsk }: Props) {
  const [question, setQuestion] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries, asking]);

  function submit() {
    const q = question.trim();
    if (!q || asking) return;
    onAsk(q);
    setQuestion("");
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    submit();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-history">
        {entries.length === 0 && !asking && (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <div className="chat-empty-title">Ask a question about your documents</div>
            <div className="chat-empty-sub">
              Upload a document on the left, then ask anything about it.
            </div>
          </div>
        )}
        {entries.map((entry) => (
          <div key={entry.id} className="chat-entry">
            <div className="question-bubble">{entry.question}</div>
            <AnswerView
              answer={entry.answer}
              sources={entry.sources}
              refused={entry.refused}
            />
          </div>
        ))}
        {asking && (
          <div className="thinking-indicator">
            <div className="dots">
              <div className="dot" />
              <div className="dot" />
              <div className="dot" />
            </div>
            Thinking…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="chat-input-row">
          <textarea
            className="chat-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents… (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={asking}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!question.trim() || asking}
          >
            {asking ? (
              <>
                <span className="spinner" />
                Asking…
              </>
            ) : (
              "Ask"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
