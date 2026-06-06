import pytest

from app.services import rag
from app.services.retrieval import RetrievedChunk


def _chunk(similarity, text="some grounded context", idx=0):
    return RetrievedChunk(
        text=text,
        document_id="doc1",
        filename="doc1.txt",
        file_type="txt",
        chunk_index=idx,
        source=f"doc1.txt [chunk {idx + 1}]",
        similarity=similarity,
    )


def test_refuses_when_no_chunks(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [])
    called = []
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: called.append(True) or "should not run",
    )

    result = rag.answer_question("anything")

    assert result.refused is True
    assert result.answer == rag.REFUSAL_MESSAGE
    assert result.sources == []
    assert called == []  # LLM must not be called


def test_refuses_when_below_threshold(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [_chunk(0.1)])
    called = []
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: called.append(True) or "x",
    )

    result = rag.answer_question("q")

    assert result.refused is True
    assert result.sources == []
    assert called == []


def test_answers_when_evidence_sufficient(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [_chunk(0.8)])
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: "The answer is grounded.",
    )

    result = rag.answer_question("q")

    assert result.refused is False
    assert result.answer == "The answer is grounded."
    assert len(result.sources) == 1
    assert result.sources[0].document_id == "doc1"
    assert result.sources[0].snippet == "some grounded context"
    assert result.sources[0].similarity == 0.8


def test_prompt_contains_context_and_question(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [_chunk(0.9, text="EVIDENCE")])

    def fake_generate(system, user_message):
        captured["system"] = system
        captured["user"] = user_message
        return "ok"

    monkeypatch.setattr("app.core.llm_client.generate", fake_generate)

    rag.answer_question("What is the capital?")

    assert "EVIDENCE" in captured["user"]
    assert "What is the capital?" in captured["user"]
    assert rag.REFUSAL_MESSAGE in captured["system"]


def test_secondary_prompt_level_refusal(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [_chunk(0.8)])
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: rag.REFUSAL_MESSAGE,
    )

    result = rag.answer_question("q")

    assert result.refused is True
    assert result.sources == []


def test_llm_error_raises_unavailable(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [_chunk(0.8)])

    def fail(system, user_message):
        raise Exception("API key invalid")

    monkeypatch.setattr("app.core.llm_client.generate", fail)

    with pytest.raises(rag.LLMUnavailableError):
        rag.answer_question("q")
