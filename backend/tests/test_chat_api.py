from fastapi.testclient import TestClient

from app.main import app
from app.services import rag

client = TestClient(app)


def test_chat_happy_path(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: _one_chunk(0.8))
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: "A grounded answer.",
    )

    response = client.post("/chat", json={"question": "What does it say?"})

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["answer"] == "A grounded answer."
    assert len(body["sources"]) == 1
    src = body["sources"][0]
    assert set(src.keys()) == {
        "document_id",
        "filename",
        "file_type",
        "chunk_index",
        "source",
        "snippet",
        "similarity",
    }


def test_chat_refusal_does_not_call_llm(monkeypatch):
    monkeypatch.setattr("app.services.rag.retrieve", lambda q: [])
    called = []
    monkeypatch.setattr(
        "app.core.llm_client.generate",
        lambda system, user_message: called.append(True) or "x",
    )

    response = client.post("/chat", json={"question": "Unknown topic?"})

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is True
    assert body["answer"] == rag.REFUSAL_MESSAGE
    assert body["sources"] == []
    assert called == []


def test_chat_empty_question_rejected():
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422


def _one_chunk(similarity):
    from app.services.retrieval import RetrievedChunk

    return [
        RetrievedChunk(
            text="grounded context text",
            document_id="doc1",
            filename="doc1.txt",
            file_type="txt",
            chunk_index=0,
            source="doc1.txt [chunk 1]",
            similarity=similarity,
        )
    ]
