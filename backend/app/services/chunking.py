from dataclasses import dataclass

from app.config import settings


@dataclass
class Chunk:
    text: str
    document_id: str
    filename: str
    file_type: str
    chunk_index: int
    source: str


def chunk_text(
    text: str,
    document_id: str,
    filename: str,
    file_type: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap

    if not text.strip():
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = start + size
        chunks.append(
            Chunk(
                text=text[start:end],
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                chunk_index=index,
                source=f"{filename} [chunk {index + 1}]",
            )
        )
        if end >= len(text):
            break
        start = end - overlap
        index += 1

    return chunks
