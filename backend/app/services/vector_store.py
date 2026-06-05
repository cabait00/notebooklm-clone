from pathlib import Path

from app.config import settings
from app.services.chunking import Chunk

_client = None
_COLLECTION_NAME = "document_chunks"


def add_document_chunks(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    if not chunks:
        return
    collection = _get_collection()
    collection.add(
        ids=[f"{c.document_id}_chunk_{c.chunk_index}" for c in chunks],
        documents=[c.text for c in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": c.document_id,
                "filename": c.filename,
                "file_type": c.file_type,
                "chunk_index": c.chunk_index,
                "source": c.source,
            }
            for c in chunks
        ],
    )


def query(query_embedding: list[float], top_k: int) -> list[dict]:
    collection = _get_collection()
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    # Chroma returns parallel lists wrapped in an outer list (one per query).
    documents = result["documents"][0] if result["documents"] else []
    metadatas = result["metadatas"][0] if result["metadatas"] else []
    distances = result["distances"][0] if result["distances"] else []

    hits = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        hits.append(
            {
                "text": text,
                "metadata": metadata,
                # Collection uses cosine space, so similarity = 1 - distance.
                "similarity": 1.0 - distance,
            }
        )
    return hits


def delete_document(document_id: str) -> None:
    collection = _get_collection()
    collection.delete(where={"document_id": document_id})


def _get_collection():
    global _client
    if _client is None:
        # Lazy import — avoids loading chromadb during tests that mock this module
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
