from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    character_count: int
    chunk_count: int = 0
    status: str
