import pytest
from fastapi.testclient import TestClient

from app import config as config_module
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config_module.settings, "upload_dir", str(tmp_path))
    # Patch expensive services so tests never load torch or chromadb
    monkeypatch.setattr(
        "app.services.embeddings.embed_texts",
        lambda texts: [[0.0] * 384 for _ in texts],
    )
    monkeypatch.setattr(
        "app.services.vector_store.add_document_chunks",
        lambda chunks, embeddings: None,
    )
    monkeypatch.setattr(
        "app.services.vector_store.delete_document",
        lambda document_id: None,
    )


def test_upload_txt_returns_metadata():
    response = client.post(
        "/documents",
        files={"file": ("sample.txt", b"Hello world. This is a test document.", "text/plain")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "sample.txt"
    assert body["file_type"] == "txt"
    assert body["character_count"] > 0
    assert body["status"] == "processed"
    assert "document_id" in body


def test_upload_md_returns_metadata():
    response = client.post(
        "/documents",
        files={"file": ("notes.md", b"# Title\n\nSome markdown content.", "text/markdown")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "notes.md"
    assert body["file_type"] == "md"
    assert body["character_count"] > 0


def test_upload_unsupported_type_rejected():
    response = client.post(
        "/documents",
        files={"file": ("data.csv", b"col1,col2\n1,2", "text/csv")},
    )
    assert response.status_code == 422
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_file_rejected():
    response = client.post(
        "/documents",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 422
    assert "No text could be extracted" in response.json()["detail"]


def test_list_documents_returns_uploaded():
    client.post(
        "/documents",
        files={"file": ("doc.txt", b"Some document content here.", "text/plain")},
    )
    response = client.get("/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 1
    assert docs[0]["filename"] == "doc.txt"


def test_list_documents_empty_initially():
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_upload_returns_chunk_count():
    # ~1800 chars — enough for 2 chunks at chunk_size=900, overlap=150
    content = ("This is a sentence used to fill the document for chunking. " * 30).encode()
    response = client.post(
        "/documents",
        files={"file": ("long.txt", content, "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["chunk_count"] >= 1


def test_delete_document_returns_204():
    upload = client.post(
        "/documents",
        files={"file": ("to_delete.txt", b"Content to be deleted.", "text/plain")},
    )
    assert upload.status_code == 201
    doc_id = upload.json()["document_id"]

    response = client.delete(f"/documents/{doc_id}")
    assert response.status_code == 204


def test_delete_removes_document_from_list():
    upload = client.post(
        "/documents",
        files={"file": ("deletable.txt", b"This document will be removed.", "text/plain")},
    )
    doc_id = upload.json()["document_id"]

    client.delete(f"/documents/{doc_id}")

    listing = client.get("/documents")
    ids = [d["document_id"] for d in listing.json()]
    assert doc_id not in ids


def test_delete_nonexistent_document_returns_404():
    response = client.delete("/documents/nonexistent-id-00000000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
