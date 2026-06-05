from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, Source
from app.services import rag

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = rag.answer_question(request.question)
    return ChatResponse(
        answer=result.answer,
        sources=[Source(**vars(s)) for s in result.sources],
        refused=result.refused,
    )
