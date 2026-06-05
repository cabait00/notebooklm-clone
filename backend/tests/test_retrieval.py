import pytest

from app.services import retrieval


def _meta(doc_id, idx):
    return {
        "document_id": doc_id,
        "filename": f"{doc_id}.txt",
        "file_type": "txt",
        "chunk_index": idx,
        "source": f"{doc_id}.txt [chunk {idx + 1}]",
    }


@pytest.fixture(autouse=True)
def mock_embeddings(monkeypatch):
    monkeypatch.setattr(
        "app.services.embeddings.embed_texts",
        lambda texts: [[0.1, 0.2, 0.3] for _ in texts],
    )


def test_retrieve_maps_hits_to_chunks(monkeypatch):
    hits = [
        {"text": "alpha", "metadata": _meta("docA", 0), "similarity": 0.9},
        {"text": "beta", "metadata": _meta("docB", 1), "similarity": 0.5},
    ]
    monkeypatch.setattr("app.services.vector_store.query", lambda emb, k: hits)

    chunks = retrieval.retrieve("some question")

    assert len(chunks) == 2
    assert chunks[0].text == "alpha"
    assert chunks[0].document_id == "docA"
    assert chunks[0].chunk_index == 0
    assert chunks[0].source == "docA.txt [chunk 1]"
    assert chunks[0].similarity == 0.9


def test_retrieve_sorts_by_similarity_desc(monkeypatch):
    hits = [
        {"text": "low", "metadata": _meta("docA", 0), "similarity": 0.3},
        {"text": "high", "metadata": _meta("docB", 0), "similarity": 0.8},
    ]
    monkeypatch.setattr("app.services.vector_store.query", lambda emb, k: hits)

    chunks = retrieval.retrieve("q")

    assert [c.similarity for c in chunks] == [0.8, 0.3]


def test_retrieve_empty_returns_empty_list(monkeypatch):
    monkeypatch.setattr("app.services.vector_store.query", lambda emb, k: [])

    assert retrieval.retrieve("q") == []
