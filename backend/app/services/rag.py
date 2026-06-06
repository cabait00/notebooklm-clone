from dataclasses import dataclass

from app.config import settings
from app.core import llm_client
from app.services.retrieval import RetrievedChunk, retrieve

REFUSAL_MESSAGE = (
    "I could not find enough evidence in the uploaded documents to answer this question."
)


class LLMUnavailableError(Exception):
    """Raised when the LLM service fails (bad key, rate limit, network, etc.)."""

SNIPPET_LENGTH = 200

SYSTEM_PROMPT = (
    "You are a careful assistant that answers questions strictly from the provided "
    "document context.\n"
    "Rules:\n"
    "- Answer ONLY using the provided context. Do not use prior or world knowledge.\n"
    "- If the context does not contain enough information to answer, reply with EXACTLY "
    f"this sentence and nothing else: {REFUSAL_MESSAGE}\n"
    "- Be concise and base every statement on the context."
)


@dataclass
class Source:
    document_id: str
    filename: str
    file_type: str
    chunk_index: int
    source: str
    snippet: str
    similarity: float


@dataclass
class RagResult:
    answer: str
    sources: list[Source]
    refused: bool


def answer_question(question: str) -> RagResult:
    chunks = retrieve(question)

    # Primary refusal mechanism: the retrieval gate. No LLM call when evidence is weak.
    if not chunks or chunks[0].similarity < settings.min_similarity:
        return RagResult(answer=REFUSAL_MESSAGE, sources=[], refused=True)

    prompt = _build_prompt(question, chunks)
    try:
        answer = llm_client.generate(system=SYSTEM_PROMPT, user_message=prompt).strip()
    except Exception as exc:
        raise LLMUnavailableError("LLM call failed") from exc

    # Secondary safety mechanism: honour a prompt-level refusal from the model.
    if answer == REFUSAL_MESSAGE:
        return RagResult(answer=REFUSAL_MESSAGE, sources=[], refused=True)

    return RagResult(answer=answer, sources=_to_sources(chunks), refused=False)


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context_blocks = "\n\n".join(
        f"[Source {i + 1}: {chunk.source}]\n{chunk.text}"
        for i, chunk in enumerate(chunks)
    )
    return f"Context:\n{context_blocks}\n\nQuestion: {question}"


def _to_sources(chunks: list[RetrievedChunk]) -> list[Source]:
    return [
        Source(
            document_id=chunk.document_id,
            filename=chunk.filename,
            file_type=chunk.file_type,
            chunk_index=chunk.chunk_index,
            source=chunk.source,
            snippet=chunk.text[:SNIPPET_LENGTH],
            similarity=chunk.similarity,
        )
        for chunk in chunks
    ]
