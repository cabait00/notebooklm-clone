from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    character_count: int
    chunk_count: int = 0
    status: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class Source(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunk_index: int
    source: str
    snippet: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    refused: bool
