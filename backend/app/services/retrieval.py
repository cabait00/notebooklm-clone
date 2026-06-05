from dataclasses import dataclass

from app.config import settings
from app.services import embeddings as embedding_service
from app.services import vector_store


@dataclass
class RetrievedChunk:
    text: str
    document_id: str
    filename: str
    file_type: str
    chunk_index: int
    source: str
    similarity: float


def retrieve(question: str, top_k: int | None = None) -> list[RetrievedChunk]:
    k = top_k if top_k is not None else settings.top_k

    query_embedding = embedding_service.embed_texts([question])[0]
    hits = vector_store.query(query_embedding, k)

    chunks = [
        RetrievedChunk(
            text=hit["text"],
            document_id=hit["metadata"]["document_id"],
            filename=hit["metadata"]["filename"],
            file_type=hit["metadata"]["file_type"],
            chunk_index=hit["metadata"]["chunk_index"],
            source=hit["metadata"]["source"],
            similarity=hit["similarity"],
        )
        for hit in hits
    ]
    # Chroma already returns results sorted by distance; sort defensively.
    chunks.sort(key=lambda c: c.similarity, reverse=True)
    return chunks
